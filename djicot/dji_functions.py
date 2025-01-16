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

"""DJI OcuSync Decoding Functions."""

import logging
import os
import struct

Logger = logging.getLogger(__name__)

DJI_PAYLOAD = {
    "serial_number": None,
    "device_type": None,
    "device_type_8": None,
    "op_lat": None,
    "op_lon": None,
    "uas_lat": None,
    "uas_lon": None,
    "height": None,
    "altitude": None,
    "home_lat": None,
    "home_lon": None,
    "freq": None,
    "speed_e": None,
    "speed_n": None,
    "speed_u": None,
    "rssi": None,
    "software": "DJICOT",
}


def parse_frame(frame):
    """
    Parses a given OcuSync frame and extracts its components.

    Args:
        frame (bytes): The input frame to be parsed.

    Returns:
        tuple: A tuple containing the package type (int) and the data (bytes).

    The frame is expected to have the following structure:
        - The first 2 bytes are the frame header.
        - The 3rd byte is the package type.
        - The 4th and 5th bytes represent the length of the package.
        - The remaining bytes contain the data.

    The function logs the frame, frame header, package type, length bytes, package length, and data for debugging purposes.
    """
    Logger.debug("frame=", frame)

    frame_header = frame[:2]
    package_type = frame[2]
    length_bytes = frame[3:5]
    package_length = struct.unpack("H", length_bytes)[0]
    data = frame[5 : 5 + package_length - 5]

    Logger.debug("frame_header=", frame_header)
    Logger.debug("package_type=", package_type)
    Logger.debug("length_bytes=", length_bytes)
    Logger.debug("package_length=", package_length)
    Logger.debug("data=", data)

    return package_type, data


def parse_data(data):
    payload = DJI_PAYLOAD.copy()
    try:
        payload = {
            "serial_number": data[:64].decode("utf-8").rstrip("\x00"),
            "device_type": data[64:128].decode("utf-8").rstrip("\x00"),
            "device_type_8": data[128],
            "op_lat": struct.unpack("d", data[129:137])[0],
            "op_lon": struct.unpack("d", data[137:145])[0],
            "uas_lat": struct.unpack("d", data[145:153])[0],
            "uas_lon": struct.unpack("d", data[153:161])[0],
            "height": struct.unpack("d", data[161:169])[0],
            "altitude": struct.unpack("d", data[169:177])[0],
            "home_lat": struct.unpack("d", data[177:185])[0],
            "home_lon": struct.unpack("d", data[185:193])[0],
            "freq": struct.unpack("d", data[193:201])[0],
            "speed_e": struct.unpack("d", data[201:209])[0],
            "speed_n": struct.unpack("d", data[209:217])[0],
            "speed_u": struct.unpack("d", data[217:225])[0],
            "rssi": struct.unpack("h", data[225:227])[0],
        }
    except UnicodeDecodeError as exc:
        if bool(os.getenv("DEBUG")):
            print(f"UnicodeDecodeError: {exc}")
        # If we fail to decode, it may indicate encrypted or partial data
        payload = {
            "device_type": "Unknown DJI OcuSync Format (Encrypted or Partial Data)",
            "device_type_8": 255,
        }

    return payload
