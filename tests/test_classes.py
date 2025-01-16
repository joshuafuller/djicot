#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Copyright Sensors & Signals LLC https://www.snstac.com/
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

"""DJICOT Class Tests."""

import asyncio
import unittest
from unittest.mock import patch
from djicot.classes import DJIWorker
from djicot.constants import DEFAULT_SENSOR_COT_TYPE, DEFAULT_COT_TYPE
from configparser import ConfigParser, SectionProxy
import pytest


@pytest.fixture
def config():
    config_parser = ConfigParser()
    config_parser.read_dict(
        {
            "DEFAULT": {
                "INCLUDE_TISB": "false",
                "TISB_ONLY": "false",
                "INCLUDE_ALL_CRAFT": "true",
            }
        }
    )
    return config_parser["DEFAULT"]


@pytest.fixture
def real_queue():
    return asyncio.Queue()


@pytest.fixture
def real_queue2():
    return asyncio.Queue()


@pytest.fixture
def real_worker(real_queue, real_queue2, config):
    return DJIWorker(real_queue, config, real_queue)


class MockWriter:
    """Mock CoT Event Writer."""

    def __init__(self):
        self.events = []

    async def send(self, event):
        self.events.append(event)


@pytest.fixture
def mock_writer():
    return MockWriter()


@pytest.mark.asyncio
async def test_handle_data_with_invalid_data(real_worker, real_queue):
    """Test handle_data method."""
    data = b"<dji_data/>"
    await real_worker.handle_data(data)

    event = await real_queue.get()
    print(event)
    assert b"DJICOT" in event
    assert DEFAULT_COT_TYPE.encode("UTF-8") in event


@pytest.mark.asyncio
async def test_hello_event(real_worker, real_queue):
    """Test hello_event method."""
    result = await real_worker.hello_event(init=True)
    event = await real_queue.get()
    print(event)
    assert event is not None
    assert b"CUAS" in event
    assert result is None


@pytest.mark.asyncio
async def _test_handle_data_with_valid_data(real_worker, real_queue):
    """Test handle_data method with valid data."""
    data = b"<dji_data/>"
    with patch(
        "djicot.functions.gen_dji_cot", return_value=b"<cot_event/>"
    ) as mock_func:
        result = await real_worker.handle_data(data)
        event = await real_queue.get()
        assert event == b"<cot_event/>"
        assert result is None
        mock_func.assert_any_call(data, real_worker.config, "gen_dji_cot")
        mock_func.assert_any_call(data, real_worker.config, "dji_uas_to_cot")


# @pytest.mark.asyncio
# async def test_handle_data_with_invalid_data(real_worker, real_queue):
#     """Test handle_data method with invalid data."""
#     data = b"<invalid_data/>"
#     with patch(
#         "djicot.classes.gen_dji_cot", side_effect=[None, b"<cot_event/>"]
#     ) as mock_func:
#         result = await real_worker.handle_data(data)
#         event = await real_queue.get()
#         assert event == b"<cot_event/>"
#         assert result is None
#         assert mock_func.call_count == 2
#         mock_func.assert_any_call(data, real_worker.config, "gen_dji_cot")
#         mock_func.assert_any_call(data, real_worker.config, "dji_uas_to_cot")


# @pytest.mark.asyncio
# async def test_handle_data_with_no_event(real_worker, real_queue):
#     """Test handle_data method with no event generated."""
#     data = b"<no_event_data/>"
#     with patch("djicot.classes.xml_to_cot", return_value=None) as mock_xml_to_cot:
#         result = await real_worker.handle_data(data)
#         # assert real_queue.empty()
#         assert result is None
#         assert mock_xml_to_cot.call_count == 2
#         mock_xml_to_cot.assert_any_call(data, real_worker.config, "dji_to_cot")
#         mock_xml_to_cot.assert_any_call(data, real_worker.config, "dji_range_to_cot")


# @pytest.mark.asyncio
# async def test_handle_data_invalid_decode(real_worker, real_queue):
#     """Test handle_data method with invalid decode."""
#     data = {
#         "serial_number": "3NZCJ290048m",
#         "device_type": "",
#         "device_type_8": 0,
#         "op_lat": 1671.8222513793953,
#         "op_lon": 7421.5640767075565,
#         "uas_lat": -9928.970842190301,
#         "uas_lon": -7990.694745406313,
#         "height": -2221.4,
#         "altitude": 2561.7,
#         "home_lat": 4109.836907633514,
#         "home_lon": 6294.859000876625,
#         "freq": 5796.5,
#         "speed_e": -3020.9,
#         "speed_n": 301.8,
#         "speed_u": 1307.4,
#         "rssi": -58,
#     }
#     result = await real_worker.handle_data(data)
#     assert result is None
#     # assert real_queue.empty()


if __name__ == "__main__":
    unittest.main()
