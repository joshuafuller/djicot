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

"""
DJI Drone ID to TAK Gateway.

This module serves as the entry point for the DJI to TAK Gateway application.
It imports and exposes constants, functions, and classes necessary for the
operation of the gateway.
"""

__version__ = "1.0.0"

from .constants import (  # NOQA
    DEFAULT_FEED_URL,
    DEFAULT_COT_TYPE,
    DEFAULT_SENSOR_LAT,
    DEFAULT_SENSOR_LON,
    DEFAULT_SENSOR_HAE,
    DEFAULT_SENSOR_LE,
    DEFAULT_SENSOR_CE,
    DEFAULT_SENSOR_ID,
    DEFAULT_SENSOR_NAME,
    DEFAULT_SENSOR_DETAIL,
    DEFAULT_SENSOR_STALE,
    DEFAULT_SENSOR_TYPE,
    DEFAULT_SENSOR_UID,
    DEFAULT_SENSOR_CONTACT,
    DEFAULT_SENSOR_COT_TYPE,
    DEFAULT_SENSOR_SN,
    DEFAULT_READ_BYTES,
    DEFAULT_BREAD_CRUMBS_ENABLED,
    DEFAULT_HIDE_INVALID_DATA
)

from .functions import create_tasks, xml_to_cot, handle_frame  # NOQA

from .classes import DJIWorker, NetWorker  # NOQA
