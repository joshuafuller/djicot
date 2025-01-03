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

"""DJICOT Functions."""

import asyncio
import struct
import xml.etree.ElementTree as ET

from configparser import SectionProxy
from typing import Optional, Set, Union

import pytak
import djicot


APP_NAME = "djicot"


def create_tasks(config: SectionProxy, clitool: pytak.CLITool) -> Set[pytak.Worker,]:
    """Create specific coroutine task set for this application.

    Parameters
    ----------
    config : `SectionProxy`
        Configuration options & values.
    clitool : `pytak.CLITool`
        A PyTAK Worker class instance.

    Returns
    -------
    `set`
        Set of PyTAK Worker classes for this application.
    """
    tasks = set()

    net_queue: asyncio.Queue = asyncio.Queue()

    tasks.add(djicot.DJIWorker(clitool.tx_queue, config, net_queue))
    tasks.add(djicot.NetWorker(net_queue, config))

    return tasks


def parse_frame(frame):
    frame_header = frame[:2]
    package_type = frame[2]
    length_bytes = frame[3:5]
    package_length = struct.unpack("H", length_bytes)[0]
    data = frame[5 : 5 + package_length - 5]
    return package_type, data


def parse_data(data):
    payload = {
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
    }

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
    except UnicodeDecodeError:
        # If we fail to decode, it may indicate encrypted or partial data
        payload = {
            "device_type": "Got a DJI drone with encryption",
            "device_type_8": 255,
        }

    return payload


def dji_to_cot_xml(  # NOQA pylint: disable=too-many-locals,too-many-branches,too-many-statements
    data, config: Union[SectionProxy, dict, None] = None
) -> Optional[ET.Element]:
    """
    Serialize DJI data as Cursor on Target.

    Returns
    -------
    `xml.etree.ElementTree.Element`
        Cursor-On-Target XML ElementTree object.
    """
    package_type, _data = parse_frame(data)
    if package_type != 0x01:
        return None

    parsed_data = parse_data(_data)
    print(parsed_data)

    # Extract relevant info for CoT
    lat = parsed_data.get("uas_lat", 0.0)
    lon = parsed_data.get("uas_lon", 0.0)
    uas_sn = parsed_data.get("serial_number", "")
    uas_type = parsed_data.get("device_type", "")

    if lat is None or lon is None:
        return None

    config = config or {}

    remarks_fields: list = []

    cot_type = "a-u-G"
    cot_stale: int = int(config.get("COT_STALE", pytak.DEFAULT_COT_STALE))
    cot_host_id: str = config.get("COT_HOST_ID", pytak.DEFAULT_HOST_ID)

    cuas = ET.Element("__cuas")
    cuas.set("cot_host_id", cot_host_id)
    cuas.set("uas_type", uas_type)
    cuas.set("uas_type_8", str(parsed_data.get("device_type_8")))
    cuas.set("uas_sn", str(uas_sn))
    cuas.set("freq", str(parsed_data.get("freq", 0.0)))
    cuas.set("rssi", str(parsed_data.get("rssi", 0)))
    cuas.set("speed_e", str(parsed_data.get("speed_e", 0.0)))
    cuas.set("speed_n", str(parsed_data.get("speed_n", 0.0)))
    cuas.set("speed_u", str(parsed_data.get("speed_u", 0.0)))

    cot_uid = f"DJI.{uas_sn}.uas"
    callsign = f"DJI-{uas_sn}"

    contact: ET.Element = ET.Element("contact")
    contact.set("callsign", callsign)

    track: ET.Element = ET.Element("track")
    track.set("course", parsed_data.get("course_point", "9999999.0"))
    track.set("speed", parsed_data.get("speed_point", "9999999.0"))

    detail = ET.Element("detail")

    # Remarks should always be the first sub-entity within the Detail entity.
    remarks = ET.Element("remarks")
    remarks_fields.append(f"Serial Number: {uas_sn}")
    remarks_fields.append(f"Type: {uas_type}")
    remarks_fields.append(f"Freq: {parsed_data.get('freq', 0.0)}")
    remarks_fields.append(f"RSSI: {parsed_data.get('rssi', 0)}")
    remarks_fields.append(f"Speed: {parsed_data.get('speed_e', 0.0)}")
    remarks_fields.append(f"{cot_host_id}")
    _remarks = " ".join(list(filter(None, remarks_fields)))
    remarks.text = _remarks
    detail.append(remarks)

    detail.append(contact)
    detail.append(track)
    detail.append(cuas)

    cot_d = {
        "lat": str(lat),
        "lon": str(lon),
        "ce": str(parsed_data.get("nac_p", "9999999.0")),
        "le": str(parsed_data.get("nac_v", "9999999.0")),
        "hae": str(parsed_data.get("alt_geom", "9999999.0")),
        "uid": cot_uid,
        "cot_type": cot_type,
        "stale": cot_stale,
    }
    cot = pytak.gen_cot_xml(**cot_d)
    cot.set("access", config.get("COT_ACCESS", pytak.DEFAULT_COT_ACCESS))

    _detail = cot.findall("detail")[0]
    flowtags = _detail.findall("_flow-tags_")
    detail.extend(flowtags)
    cot.remove(_detail)
    cot.append(detail)

    return cot


def dji_to_cot(
    craft: dict,
    config: Union[SectionProxy, dict, None] = None,
) -> Optional[bytes]:
    """Return CoT XML object as an XML string."""
    cot: Optional[ET.Element] = dji_to_cot_xml(craft, config)
    return (
        b"\n".join([pytak.DEFAULT_XML_DECLARATION, ET.tostring(cot)]) if cot else None
    )
