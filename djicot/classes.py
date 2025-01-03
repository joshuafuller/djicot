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

from typing import Optional
from urllib.parse import urlparse, ParseResult

import pytak
import djicot


class DJIWorker(pytak.QueueWorker):
    """Read DJI data from inputs, serialize to CoT, and put on TX queue."""

    def __init__(
        self,
        tx_queue: asyncio.Queue,
        config: dict,
        net_queue: asyncio.Queue,
    ) -> None:
        """Initialize the DJIWorker."""
        super().__init__(tx_queue, config)
        self.net_queue = net_queue

    async def handle_data(self, data) -> None:
        """Handle Data from ADS-B receiver: Render to CoT, put on TX queue."""
        event: Optional[bytes] = djicot.dji_to_cot(data, self.config)
        await self.put_queue(event)

    async def run(self, _=-1) -> None:
        """Run this Thread, Reads from Pollers."""

        self._logger.info("Running %s", self.__class__)

        while 1:
            received = await self.net_queue.get()
            if not received:
                continue
            await self.handle_data(received)


class NetWorker(pytak.QueueWorker):  # pylint: disable=too-few-public-methods
    """Read DJI Data from network and puts on queue."""

    async def handle_data(self, data) -> None:
        """Handle Data from network."""
        self.queue.put_nowait(data)

    async def run(self, _=-1) -> None:
        """Run the main process loop."""
        url: ParseResult = urlparse(
            self.config.get("FEED_URL", djicot.DEFAULT_FEED_URL)
        )

        self._logger.info("Running %s for %s", self.__class__, url.geturl())

        host, port = url.netloc.split(":")

        self._logger.debug("host=%s port=%s", host, port)

        reader, _ = await asyncio.open_connection(host, port)

        while 1:
            received = await reader.read(1024)
            await self.handle_data(received)
