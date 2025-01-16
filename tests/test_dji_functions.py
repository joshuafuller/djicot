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

"""DJICOT Function Tests."""


import struct
import unittest
from djicot.dji_functions import parse_frame, parse_data


class DJIFunctionsTestCase(unittest.TestCase):
    """
    Test class for functions... functions.
    """

    def test_parse_frame(self):
        """Test parse_frame function with valid frame data."""
        frame = bytearray(10)
        frame[:2] = b"\x01\x02"  # frame_header
        frame[2] = 0x03  # package_type
        frame[3:5] = struct.pack("H", 10)  # package_length
        frame[5:10] = b"hello"  # data

        package_type, data = parse_frame(frame)
        self.assertEqual(package_type, 0x03)
        self.assertEqual(data, b"hello")

    def test_parse_frame_with_invalid_length(self):
        """Test parse_frame function with invalid length."""
        frame = bytearray(8)
        frame[:2] = b"\x01\x02"  # frame_header
        frame[2] = 0x03  # package_type
        frame[3:5] = struct.pack("H", 10)  # package_length
        frame[5:8] = b"hel"  # data

        package_type, data = parse_frame(frame)
        self.assertEqual(package_type, 0x03)
        self.assertEqual(data, b"hel")

    def test_parse_data(self):
        """Test parse_data function with valid data."""

        data = bytearray(227)
        data[:64] = b"serial_number".ljust(64, b"\x00")
        data[64:128] = b"device_type".ljust(64, b"\x00")
        data[128] = 8
        data[129:137] = struct.pack("d", 37.7749)  # app_lat
        data[137:145] = struct.pack("d", -122.4194)  # app_lon
        data[145:153] = struct.pack("d", 37.7749)  # uas_lat
        data[153:161] = struct.pack("d", -122.4194)  # uas_lon
        data[161:169] = struct.pack("d", 100.0)  # height
        data[169:177] = struct.pack("d", 200.0)  # altitude
        data[177:185] = struct.pack("d", 37.7749)  # home_lat
        data[185:193] = struct.pack("d", -122.4194)  # home_lon
        data[193:201] = struct.pack("d", 2.4)  # freq
        data[201:209] = struct.pack("d", 10.0)  # speed_e
        data[209:217] = struct.pack("d", 5.0)  # speed_n
        data[217:225] = struct.pack("d", 1.0)  # speed_u
        data[225:227] = struct.pack("h", -50)  # rssi

        parsed_data = parse_data(data)
        self.assertEqual(parsed_data.get("serial_number"), "serial_number")
        self.assertEqual(parsed_data.get("device_type"), "device_type")
        self.assertEqual(parsed_data.get("device_type_8"), 8)
        self.assertEqual(parsed_data.get("op_lat"), 37.7749)
        self.assertEqual(parsed_data.get("op_lon"), -122.4194)
        self.assertEqual(parsed_data.get("uas_lat"), 37.7749)
        self.assertEqual(parsed_data.get("uas_lon"), -122.4194)
        self.assertEqual(parsed_data.get("height"), 100.0)
        self.assertEqual(parsed_data.get("altitude"), 200.0)
        self.assertEqual(parsed_data.get("home_lat"), 37.7749)
        self.assertEqual(parsed_data.get("home_lon"), -122.4194)
        self.assertEqual(parsed_data.get("freq"), 2.4)
        self.assertEqual(parsed_data.get("speed_e"), 10.0)
        self.assertEqual(parsed_data.get("speed_n"), 5.0)
        self.assertEqual(parsed_data.get("speed_u"), 1.0)
        self.assertEqual(parsed_data.get("rssi"), -50)

    def _test_parse_data_with_invalid_data(self):
        """Test parse_data function with invalid data."""
        data = b"invalid_data"
        parsed_data = parse_data(data)
        self.assertEqual(
            parsed_data["device_type"],
            "Unknown DJI OcuSync Format (Encrypted or Partial Data)",
        )
        self.assertEqual(parsed_data["device_type_8"], 255)

    def test_parse_frame_with_package_type_0x01(self):
        """Test parse_frame function with package_type 0x01."""
        frame = bytearray(10)
        frame[:2] = b"\x01\x02"  # frame_header
        frame[2] = 0x01  # package_type
        frame[3:5] = struct.pack("H", 10)  # package_length
        frame[5:10] = b"hello"  # data

        package_type, data = parse_frame(frame)
        self.assertEqual(package_type, 0x01)
        self.assertEqual(data, b"hello")


if __name__ == "__main__":
    unittest.main()
