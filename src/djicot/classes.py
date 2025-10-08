#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Copyright Sensors & Signals LLC https://www.snstac.com
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

"""DJICOT Class Definitions."""

import asyncio

import time

from configparser import SectionProxy
from typing import Optional, Union
from urllib.parse import urlparse, ParseResult

from pytak import QueueWorker

from djicot import xml_to_cot, handle_frame, DEFAULT_FEED_URL, DEFAULT_READ_BYTES


class DJIWorker(QueueWorker):
    """
    DJIWorker asynchronously processes DJI Drone ID data.

    This worker reads raw DJI data from an input queue, converts it to 
    Cursor on Target (CoT) XML events, and places the resulting events onto a
    transmission (TX) queue for further handling.

    Attributes:
        tx_queue (asyncio.Queue): Queue for outgoing CoT events.
        config (Union[SectionProxy, dict]): Configuration settings for the worker.
        net_queue (asyncio.Queue): Queue providing incoming raw DJI data.
    """

    def __init__(
        self,
        tx_queue: asyncio.Queue,
        config: Union[SectionProxy, dict],
        net_queue: asyncio.Queue,
    ) -> None:
        """Initializes the DJIWorker with the given TX queue, configuration, and network queue."""
        super().__init__(tx_queue, config)
        self.net_queue = net_queue

    async def handle_data(self, data) -> None:
        """Processes raw DJI Drone ID data, converts it to CoT format, and places it on the TX queue."""
        self._logger.debug("Received data: %s", data)  # Debug log for received data
        events = handle_frame(data, self.config)
        for event in events:
            await self.put_queue(event)

    async def hello_event(self, init=False):
        """Sends a "hello world" style event to the TX queue. This event is sent periodically or on initialization."""
        timer = int(time.time()) % 60 == 0
        if init or timer:
            data = f"init={init} timer={timer}"
            event: Optional[bytes] = xml_to_cot(data, self.config, "sensor_to_cot")
            await self.put_queue(event)

    async def run(self, _=-1) -> None:
        """Main execution loop of the worker. Sends periodic hello events and processes incoming data from the network queue."""
        self._logger.info("Running %s", self.__class__)

        if not self.config.get("PYTAK_NO_HELLO", False):
            await self.hello_event(init=True)

        while True:
            await self.hello_event()
            received = await self.net_queue.get()
            if not received:
                continue
            await self.handle_data(received)


class NetWorker(QueueWorker):  # pylint: disable=too-few-public-methods
    """
    A worker class that reads data from a network connection and puts it on a queue.
    """

    async def handle_data(self, data) -> None:
        """Asynchronously handles incoming data by placing it on the queue."""
        self.queue.put_nowait(data)

    async def run(self, _=-1) -> None:
        """Asynchronously runs the main loop to read data from the network and add it to the queue."""
        url: ParseResult = urlparse(self.config.get("FEED_URL", DEFAULT_FEED_URL))

        self._logger.info("Running %s for %s", self.__class__, url.geturl())

        host, port = url.netloc.split(":")

        self._logger.debug("host=%s port=%s", host, port)

        reader, _ = await asyncio.open_connection(host, port)

        read_bytes = self.config.get("READ_BYTES", DEFAULT_READ_BYTES)
        self._logger.debug("read_bytes=%s", read_bytes)

        while True:
            received = await reader.read(read_bytes)
            await self.handle_data(received)
