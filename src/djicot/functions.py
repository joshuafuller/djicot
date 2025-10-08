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
import logging
import os
import xml.etree.ElementTree as ET

from configparser import SectionProxy
from typing import Optional, Set, Union

import pytak
import djicot

from .dji_functions import parse_frame, parse_data
import pprint


APP_NAME = "djicot"
Logger = logging.getLogger(__name__)
Debug = bool(os.getenv("DEBUG", False))
if Debug:
    Logger.setLevel(logging.DEBUG)


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


def dji_uas_to_cot(
    data, config: Union[SectionProxy, dict, None] = None
) -> Optional[ET.Element]:
    """Convert DJI UAS data to CoT."""
    return gen_dji_cot(data, config, "uas")


def dji_op_to_cot(
    data, config: Union[SectionProxy, dict, None] = None
) -> Optional[ET.Element]:
    """Convert DJI Operator data to CoT."""
    return gen_dji_cot(data, config, "op")


def dji_home_to_cot(
    data, config: Union[SectionProxy, dict, None] = None
) -> Optional[ET.Element]:
    """Convert DJI Home data to CoT"""
    return gen_dji_cot(data, config, "home")

# Validate latitude and longitude
def is_valid_lat_lon(lat, lon):
    valid = False
    try:
        lat = float(lat)
        lon = float(lon)
        valid = lat != 0.0 and lon != 0.0
        if valid:
            valid = -90.0 <= lat <= 90.0 and -180.0 <= lon <= 180.0
    except (TypeError, ValueError):
        pass
    return valid


def gen_dji_cot(  # NOQA pylint: disable=too-many-locals,too-many-branches,too-many-statements
    data, config: Union[SectionProxy, dict, None] = None, leg="uas"
) -> Optional[ET.Element]:
    """
    Generate a Cursor on Target (CoT) XML Event from DJI data.

    Parameters
    ----------
    data : dict
        Dictionary containing the DJI data.
    config : Union[SectionProxy, dict, None], optional
        Configuration settings, by default None.
    leg : str, optional
        Specifies the leg type, by default "uas".

    Returns
    -------
    Optional[xml.etree.ElementTree.Element]
        The generated CoT XML ElementTree object, or None if latitude or longitude are missing.

    Notes
    -----
    - The function extracts relevant information from the DJI data and config to create a CoT XML element.
    - If latitude or longitude are missing for the "uas" leg, default sensor coordinates are used.
    - The function supports debugging output if "DEBUG" is set in the config.
    - The CoT element includes details such as sensor information, contact callsign, track data, and remarks.
    - The CoT element is generated using the pytak.gen_cot_xml() function.
    """
    config = config or {}

    # Extract relevant info for CoT
    lat = data.get(f"{leg}_lat")
    lon = data.get(f"{leg}_lon")

    if not is_valid_lat_lon(lat, lon):
        lat = None
        lon = None
    Logger.debug(f"leg={leg} lat={lat} lon={lon}")

    freq = str(data.get("freq", 0.0))
    rssi = str(data.get("rssi", -999))
    serial_number = data.get("serial_number")
    uas_sn = serial_number or freq
    uas_type = data.get("device_type", "")

    cot_type: str = str(config.get("COT_TYPE", djicot.DEFAULT_COT_TYPE))
    if leg == "op" or leg == "home":
        cot_type = str("a-u-G-U-C")

    cot_uid = f"DJI.{uas_sn}.{leg}"
    callsign = f"{uas_sn}.{leg}"
    ce = str(data.get("nac_p", "9999999.0"))

    if lat is None or lon is None:
        if leg == "op" or leg == "home":
            Logger.debug(f"No {leg} lat/lon")
            return None
        elif leg == "uas":
            lat = config.get("SENSOR_LAT", djicot.DEFAULT_SENSOR_LAT)
            lon = config.get("SENSOR_LON", djicot.DEFAULT_SENSOR_LON)
            cot_type = str("a-u-A-M-H-Q")
            callsign = f"{callsign} (Range)"
            ce = 1000.0 * abs(int(rssi))
            Logger.debug(f"No UAS lat/lon, using sensor lat/lon: {lat}, {lon}")

    remarks_fields: list = []

    cot_stale: int = int(config.get("COT_STALE", pytak.DEFAULT_COT_STALE))
    cot_host_id: str = config.get("COT_HOST_ID", pytak.DEFAULT_HOST_ID)
    sensor_id = str(config.get("SENSOR_ID", djicot.DEFAULT_SENSOR_ID))

    cuas = ET.Element("__cuas")
    cuas.set("sensor_id", sensor_id)
    cuas.set("sensor_sn", str(config.get("SENSOR_SN", djicot.DEFAULT_SENSOR_SN)))
    cuas.set("sensor_type", str(config.get("SENSOR_TYPE", djicot.DEFAULT_SENSOR_TYPE)))
    cuas.set("sensor_name", str(config.get("SENSOR_NAME", djicot.DEFAULT_SENSOR_NAME)))
    cuas.set("cot_host_id", cot_host_id)
    cuas.set("uas_type", uas_type)
    cuas.set("uas_type_8", str(data.get("device_type_8")))
    cuas.set("uas_sn", str(uas_sn))
    cuas.set("freq", freq)
    cuas.set("rssi", rssi)
    cuas.set("speed_e", str(data.get("speed_e", 0.0)))
    cuas.set("speed_n", str(data.get("speed_n", 0.0)))
    cuas.set("speed_u", str(data.get("speed_u", 0.0)))

    contact: ET.Element = ET.Element("contact")
    contact.set("callsign", callsign)

    track: ET.Element = ET.Element("track")
    track.set("course", data.get("course_point", "9999999.0"))
    track.set("speed", data.get("speed_point", "9999999.0"))

    detail = ET.Element("detail")

    # Remarks should always be the first sub-entity within the Detail entity.
    remarks = ET.Element("remarks")
    remarks_fields.append(f"sn={uas_sn}")
    remarks_fields.append(f"({uas_type})")
    remarks_fields.append(f"freq={data.get('freq', 0.0)}")
    remarks_fields.append(f"rss={data.get('rssi', 0)}")
    remarks_fields.append(f"speed={data.get('speed_e', 0.0)}")
    remarks_fields.append(f"sensor_id={sensor_id}")
    remarks_fields.append(f"host_id={cot_host_id}")
    _remarks = " ".join(list(filter(None, remarks_fields)))
    remarks.text = _remarks
    detail.append(remarks)

    detail.append(contact)
    detail.append(track)
    detail.append(cuas)

    le = str(data.get("nac_v", "9999999.0"))
    hae = str(data.get("alt_geom", "9999999.0"))

    cot_d = {
        "lat": str(lat),
        "lon": str(lon),
        "ce": ce,
        "le": le,
        "hae": hae,
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


def sensor_to_cot(
    data, config: Union[SectionProxy, dict, None] = None
) -> Optional[ET.Element]:
    """Create a CoT Event for the Sensor.

    Parameters
    ----------
    data : dict
        Dictionary containing the sensor data.
    config : Union[SectionProxy, dict, None], optional
        Configuration settings, by default None.

    Returns
    -------
    Optional[xml.etree.ElementTree.Element]
        The generated CoT XML ElementTree object, or None if latitude or longitude are missing.

    Notes
    -----
    - The function extracts relevant information from the sensor data and config to create a CoT XML element.
    - If latitude or longitude are missing, the function returns None.
    - The CoT element includes details such as sensor information, contact callsign, and remarks.
    - The CoT element is generated using the pytak.gen_cot_xml() function.
    """
    config = config or {}

    lat = config.get("SENSOR_LAT", djicot.DEFAULT_SENSOR_LAT)
    lon = config.get("SENSOR_LON", djicot.DEFAULT_SENSOR_LON)

    if lat is None or lon is None:
        Logger.debug("No Sensor Lat/Lon")
        return None

    sensor_id = config.get("SENSOR_ID", djicot.DEFAULT_SENSOR_ID)
    sensor_sn = config.get("SENSOR_SN", djicot.DEFAULT_SENSOR_SN)
    sensor_type = config.get("SENSOR_TYPE", djicot.DEFAULT_SENSOR_TYPE)

    cot_host_id: str = config.get("COT_HOST_ID", pytak.DEFAULT_HOST_ID)

    cot_uid = config.get("SENSOR_UID", f"CUAS-{sensor_type}-{sensor_sn}-{cot_host_id}")
    callsign = config.get("SENSOR_CALLSIGN", f"CUAS-{sensor_type}-{sensor_sn}")

    cot_type = config.get("SENSOR_COT_TYPE", djicot.DEFAULT_SENSOR_COT_TYPE)
    cot_stale = config.get("SENSOR_STALE", djicot.DEFAULT_SENSOR_STALE)

    cuas = ET.Element("__cuas")
    cuas.set("sensor_id", sensor_id)
    cuas.set("sensor_sn", sensor_sn)
    cuas.set("sensor_type", sensor_type)
    cuas.set("cot_host_id", cot_host_id)

    contact: ET.Element = ET.Element("contact")
    contact.set("callsign", callsign)

    detail = ET.Element("detail")

    # Remarks should always be the first sub-entity within the Detail entity.
    remarks = ET.Element("remarks")
    remarks.text = f"sensor_id={sensor_id} sensor_sn={sensor_sn} sensor_type={sensor_type} cot_host_id={cot_host_id}: {data}"

    detail.append(remarks)
    detail.append(contact)
    detail.append(cuas)

    cot_d = {
        "lat": str(lat),
        "lon": str(lon),
        "ce": str(config.get("SENSOR_CE", djicot.DEFAULT_SENSOR_CE)),
        "le": str(config.get("SENSOR_LE", djicot.DEFAULT_SENSOR_LE)),
        "hae": str(config.get("SENSOR_HAE", djicot.DEFAULT_SENSOR_HAE)),
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


def xml_to_cot(
    data: dict, config: Union[SectionProxy, dict, None] = None, func=None
) -> Optional[bytes]:
    """Convert data to a CoT XML string using the specified function."""
    cot: Optional[ET.Element] = getattr(djicot.functions, func)(data, config)
    return (
        b"\n".join([pytak.DEFAULT_XML_DECLARATION, ET.tostring(cot)]) if cot is not None else None
    )


def handle_frame(
    frame: bytearray, config: Union[SectionProxy, dict, None] = None
) -> list:
    """
    Parse a DJI Drone ID frame and convert the parsed data into CoT (Cursor on Target) event XML bytes.

    Parameters
    ----------
    frame : bytearray
        The raw DJI Drone ID frame to process.
    config : Union[SectionProxy, dict, None], optional
        Configuration options and values, by default None.

    Returns
    -------
    list
        List of CoT event XML bytes generated from the parsed DJI Drone ID data.

    Notes
    -----
    - This function parses the input frame, extracts the relevant data, and attempts to generate CoT events
      for UAS, operator, and home positions using the corresponding conversion functions.
    - If parsing fails or the data is invalid, warnings are logged and an empty list may be returned.
    """
    config = config or {}
    events = []
    package_type = None
    data = None
    parsed_data = {}

    try:
        package_type, data = parse_frame(frame)
    except Exception as exc:
        Logger.warning(f"Error parsing DJI frame: {exc}")

    if package_type != 0x01:
        Logger.warning(f"Invalid DJI package type: {package_type}")

    if not data:
        Logger.warning("No DJI data")
    else:
        try:
            parsed_data = parse_data(data)
        except Exception as exc:
            Logger.warning(f"Error parsing DJI data: {exc}")

    Logger.debug(f"Parsed DJI data: {parsed_data}")

    funcs = ["dji_uas_to_cot", "dji_op_to_cot", "dji_home_to_cot"]
    for func in funcs:
        event: Optional[bytes] = xml_to_cot(parsed_data, config, func)
        if event:
            events.append(event)

    return events
