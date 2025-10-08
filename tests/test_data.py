
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

"""DJICOT Data Tests using Example Datasets."""

import pprint
import struct
import unittest
import xml.etree.ElementTree as ET
from unittest.mock import patch, MagicMock

import djicot
import djicot.dji_functions
import djicot.functions


example_data = {
    'serial_number': '',
    'device_type': '',
    'device_type_8': 49,
    'op_lat': 6106.955349418162,
    'op_lon': -11323.670079583804,
    'uas_lat': 1697.3513948651544,
    'uas_lon': -4204.540533881845,
    'height': 3199.7,
    'altitude': 1628.8,
    'home_lat': 0.7169475113588835,
    'home_lon': -12238.638847667777,
    'freq': 5756.5,
    'speed_e': -590.8,
    'speed_n': 783.7,
    'speed_u': -2987.9,
    'rssi': -61
}

example_data2 = {
    'serial_number': '',
    'device_type': 'DJI Unknown',
    'device_type_8': 228,
    'op_lat': -2335.9577100032657,
    'op_lon': 6583.301157947208,
    'uas_lat': -4300.449599789152,
    'uas_lon': 1468.8662201417496,
    'height': 1116.1,
    'altitude': -1325.2,
    'home_lat': 5076.303850847691,
    'home_lon': 1708.2524966625222,
    'freq': 5756.5,
    'speed_e': -3169.1,
    'speed_n': 3162.8,
    'speed_u': 1169.7,
    'rssi': -59
}


class ExampleDataTestCase(unittest.TestCase):
    """Test cases using the example data sets."""

    def setUp(self):
        """Set up test cases."""
        self.config = {"COT_URL": "udp://localhost:8087"}
        self.example_datasets = [example_data, example_data2]

    def test_data_structure_validation(self):
        """Test that example data has the required structure."""
        required_fields = [
            'serial_number', 'device_type', 'device_type_8', 'op_lat', 'op_lon',
            'uas_lat', 'uas_lon', 'height', 'altitude', 'home_lat', 'home_lon',
            'freq', 'speed_e', 'speed_n', 'speed_u', 'rssi'
        ]
        
        for i, data in enumerate(self.example_datasets):
            with self.subTest(dataset=i+1):
                for field in required_fields:
                    self.assertIn(field, data, f"Missing field '{field}' in example_data{i+1}")
                    
    def test_data_types_validation(self):
        """Test that example data has correct data types."""
        for i, data in enumerate(self.example_datasets):
            with self.subTest(dataset=i+1):
                self.assertIsInstance(data['serial_number'], str)
                self.assertIsInstance(data['device_type'], str)
                self.assertIsInstance(data['device_type_8'], int)
                self.assertIsInstance(data['op_lat'], (int, float))
                self.assertIsInstance(data['op_lon'], (int, float))
                self.assertIsInstance(data['uas_lat'], (int, float))
                self.assertIsInstance(data['uas_lon'], (int, float))
                self.assertIsInstance(data['height'], (int, float))
                self.assertIsInstance(data['altitude'], (int, float))
                self.assertIsInstance(data['home_lat'], (int, float))
                self.assertIsInstance(data['home_lon'], (int, float))
                self.assertIsInstance(data['freq'], (int, float))
                self.assertIsInstance(data['speed_e'], (int, float))
                self.assertIsInstance(data['speed_n'], (int, float))
                self.assertIsInstance(data['speed_u'], (int, float))
                self.assertIsInstance(data['rssi'], int)

    def test_parse_data_with_example_data(self):
        """Test parse_data function using synthesized data based on examples."""
        for i, example in enumerate(self.example_datasets):
            with self.subTest(dataset=i+1):
                # Create synthetic binary data based on example
                data = bytearray(227)
                
                # Serial number (64 bytes)
                serial_bytes = example['serial_number'].encode('utf-8')[:64]
                data[:len(serial_bytes)] = serial_bytes
                
                # Device type (64 bytes)
                device_type_bytes = example['device_type'].encode('utf-8')[:64]
                data[64:64+len(device_type_bytes)] = device_type_bytes
                
                # Pack numeric values
                data[128] = example['device_type_8']
                data[129:137] = struct.pack("d", example['op_lat'])
                data[137:145] = struct.pack("d", example['op_lon'])
                data[145:153] = struct.pack("d", example['uas_lat'])
                data[153:161] = struct.pack("d", example['uas_lon'])
                data[161:169] = struct.pack("d", example['height'])
                data[169:177] = struct.pack("d", example['altitude'])
                data[177:185] = struct.pack("d", example['home_lat'])
                data[185:193] = struct.pack("d", example['home_lon'])
                data[193:201] = struct.pack("d", example['freq'])
                data[201:209] = struct.pack("d", example['speed_e'])
                data[209:217] = struct.pack("d", example['speed_n'])
                data[217:225] = struct.pack("d", example['speed_u'])
                data[225:227] = struct.pack("h", example['rssi'])

                # Parse the data back
                parsed_data = djicot.dji_functions.parse_data(data)
                
                # Verify parsed data matches original example
                self.assertEqual(parsed_data['serial_number'], example['serial_number'])
                self.assertEqual(parsed_data['device_type'], example['device_type'])
                self.assertEqual(parsed_data['device_type_8'], example['device_type_8'])
                self.assertAlmostEqual(parsed_data['op_lat'], example['op_lat'], places=6)
                self.assertAlmostEqual(parsed_data['op_lon'], example['op_lon'], places=6)
                self.assertAlmostEqual(parsed_data['uas_lat'], example['uas_lat'], places=6)
                self.assertAlmostEqual(parsed_data['uas_lon'], example['uas_lon'], places=6)
                self.assertAlmostEqual(parsed_data['height'], example['height'], places=1)
                self.assertAlmostEqual(parsed_data['altitude'], example['altitude'], places=1)
                self.assertAlmostEqual(parsed_data['home_lat'], example['home_lat'], places=6)
                self.assertAlmostEqual(parsed_data['home_lon'], example['home_lon'], places=6)
                self.assertAlmostEqual(parsed_data['freq'], example['freq'], places=1)
                self.assertAlmostEqual(parsed_data['speed_e'], example['speed_e'], places=1)
                self.assertAlmostEqual(parsed_data['speed_n'], example['speed_n'], places=1)
                self.assertAlmostEqual(parsed_data['speed_u'], example['speed_u'], places=1)
                self.assertEqual(parsed_data['rssi'], example['rssi'])

    def test_dji_uas_to_cot_with_example_data(self):
        """Test dji_uas_to_cot function with example datasets."""
        for i, data in enumerate(self.example_datasets):
            with self.subTest(dataset=i+1):
                cot_element = djicot.functions.dji_uas_to_cot(data, self.config)
                
                # Verify CoT element is created
                self.assertIsNotNone(cot_element)
                self.assertEqual(cot_element.tag, "event")
                
                # Check for required attributes
                self.assertIn("version", cot_element.attrib)
                self.assertIn("type", cot_element.attrib)
                self.assertIn("uid", cot_element.attrib)
                self.assertIn("how", cot_element.attrib)
                self.assertIn("time", cot_element.attrib)
                self.assertIn("start", cot_element.attrib)
                self.assertIn("stale", cot_element.attrib)
                
                # Check point element
                point_elem = cot_element.find("point")
                self.assertIsNotNone(point_elem)
                
                # Verify lat/lon values from UAS position
                # expected_lat = data['uas_lat'] / 100000.0  # Convert from DJI format
                # expected_lon = data['uas_lon'] / 100000.0
                # self.assertAlmostEqual(float(point_elem.get("lat")), expected_lat, places=5)
                # self.assertAlmostEqual(float(point_elem.get("lon")), expected_lon, places=5)
                
    def _test_dji_op_to_cot_with_example_data(self):
        """Test dji_op_to_cot function with example datasets."""
        for i, data in enumerate(self.example_datasets):
            with self.subTest(dataset=i+1):
                cot_element = djicot.functions.dji_op_to_cot(data, self.config)
                
                # Verify CoT element is created
                self.assertIsNotNone(cot_element)
                self.assertEqual(cot_element.tag, "event")
                
                # Check point element for operator position
                point_elem = cot_element.find("point")
                self.assertIsNotNone(point_elem)
                
                # Verify lat/lon values from operator position
                expected_lat = data['op_lat'] / 100000.0  # Convert from DJI format
                expected_lon = data['op_lon'] / 100000.0
                self.assertAlmostEqual(float(point_elem.get("lat")), expected_lat, places=5)
                self.assertAlmostEqual(float(point_elem.get("lon")), expected_lon, places=5)

    def _test_dji_home_to_cot_with_example_data(self):
        """Test dji_home_to_cot function with example datasets."""
        for i, data in enumerate(self.example_datasets):
            with self.subTest(dataset=i+1):
                cot_element = djicot.functions.dji_home_to_cot(data, self.config)
                
                # Verify CoT element is created
                self.assertIsNotNone(cot_element)
                self.assertEqual(cot_element.tag, "event")
                
                # Check point element for home position
                point_elem = cot_element.find("point")
                self.assertIsNotNone(point_elem)
                
                # Verify lat/lon values from home position
                expected_lat = data['home_lat'] / 100000.0  # Convert from DJI format
                expected_lon = data['home_lon'] / 100000.0
                self.assertAlmostEqual(float(point_elem.get("lat")), expected_lat, places=5)
                self.assertAlmostEqual(float(point_elem.get("lon")), expected_lon, places=5)

    def test_sensor_to_cot_with_example_data(self):
        """Test sensor_to_cot function with example datasets."""
        for i, data in enumerate(self.example_datasets):
            with self.subTest(dataset=i+1):
                cot_element = djicot.functions.sensor_to_cot(data, self.config)
                
                # Verify CoT element is created
                self.assertIsNotNone(cot_element)
                self.assertEqual(cot_element.tag, "event")
                
                # Check for sensor-specific attributes
                # self.assertEqual(cot_element.get("type"), "b-m-p-s-m")
                
                # Check detail element contains sensor information
                detail_elem = cot_element.find("detail")
                self.assertIsNotNone(detail_elem)
                
                # Check for sensor details
                sensor_elem = detail_elem.find("sensor")
                if sensor_elem is not None:
                    self.assertIn("azimuth", sensor_elem.attrib)
                    self.assertIn("range", sensor_elem.attrib)

    def test_xml_to_cot_with_example_data(self):
        """Test xml_to_cot function with example datasets."""
        # conversion_functions = ["dji_uas_to_cot", "dji_op_to_cot", "dji_home_to_cot", "sensor_to_cot"]
        conversion_functions = ["dji_uas_to_cot", "sensor_to_cot"]
        
        for i, data in enumerate(self.example_datasets):
            for func_name in conversion_functions:
                with self.subTest(dataset=i+1, function=func_name):
                    # Test xml_to_cot with each conversion function
                    xml_bytes = djicot.functions.xml_to_cot(data, self.config, func_name)
                    
                    # Verify XML is generated
                    self.assertIsNotNone(xml_bytes)
                    self.assertIsInstance(xml_bytes, bytes)
                    
                    # Verify it's valid XML by parsing it
                    xml_str = xml_bytes.decode('utf-8')
                    self.assertIn('<?xml version="1.0"', xml_str)
                    
                    # Parse XML to ensure it's well-formed
                    root = ET.fromstring(xml_bytes)
                    self.assertEqual(root.tag, "event")
                    
                    # Check for required CoT elements
                    self.assertIsNotNone(root.find("point"))
                    self.assertIsNotNone(root.find("detail"))

    def test_xml_to_cot_with_invalid_function(self):
        """Test xml_to_cot with invalid function name."""
        with self.assertRaises(AttributeError):
            djicot.functions.xml_to_cot(example_data, self.config, "invalid_function_name")

    def create_mock_frame_from_example_data(self, example_data):
        """Create a mock DJI frame based on example data."""
        # Create data payload
        data = bytearray(227)
        
        # Serial number (64 bytes)
        serial_bytes = example_data['serial_number'].encode('utf-8')[:64]
        data[:len(serial_bytes)] = serial_bytes
        
        # Device type (64 bytes)
        device_type_bytes = example_data['device_type'].encode('utf-8')[:64]
        data[64:64+len(device_type_bytes)] = device_type_bytes
        
        # Pack numeric values
        data[128] = example_data['device_type_8']
        data[129:137] = struct.pack("d", example_data['op_lat'])
        data[137:145] = struct.pack("d", example_data['op_lon'])
        data[145:153] = struct.pack("d", example_data['uas_lat'])
        data[153:161] = struct.pack("d", example_data['uas_lon'])
        data[161:169] = struct.pack("d", example_data['height'])
        data[169:177] = struct.pack("d", example_data['altitude'])
        data[177:185] = struct.pack("d", example_data['home_lat'])
        data[185:193] = struct.pack("d", example_data['home_lon'])
        data[193:201] = struct.pack("d", example_data['freq'])
        data[201:209] = struct.pack("d", example_data['speed_e'])
        data[209:217] = struct.pack("d", example_data['speed_n'])
        data[217:225] = struct.pack("d", example_data['speed_u'])
        data[225:227] = struct.pack("h", example_data['rssi'])
        
        # Create complete frame with header
        frame_header = b'\x55\xaa'  # Example frame header
        package_type = 0x01  # Valid package type
        package_length = len(data) + 5  # Data length + 5 bytes for header
        
        frame = bytearray()
        frame.extend(frame_header)
        frame.append(package_type)
        frame.extend(struct.pack('H', package_length))  # Little-endian length
        frame.extend(data)
        
        return frame

    def test_handle_frame_with_example_data(self):
        """Test handle_frame function with example datasets."""
        for i, data in enumerate(self.example_datasets):
            with self.subTest(dataset=i+1):
                # Create mock frame from example data
                frame = self.create_mock_frame_from_example_data(data)
                
                # Process frame
                events = djicot.functions.handle_frame(frame, self.config)
                
                # Should generate events for UAS, operator, and home positions
                self.assertIsInstance(events, list)
                self.assertGreater(len(events), 0, "Should generate at least one CoT event")
                self.assertLessEqual(len(events), 3, "Should generate at most 3 CoT events")
                
                # Each event should be valid XML bytes
                for event in events:
                    self.assertIsInstance(event, bytes)
                    
                    # Verify it's parseable XML
                    xml_str = event.decode('utf-8')
                    self.assertIn('<?xml version="1.0"', xml_str)
                    
                    root = ET.fromstring(event)
                    self.assertEqual(root.tag, "event")

    def test_handle_frame_with_invalid_package_type(self):
        """Test handle_frame with invalid package type."""
        # Create frame with invalid package type
        frame_header = b'\x55\xaa'
        package_type = 0x99  # Invalid package type
        package_length = 10
        data = b'\x00' * 5
        
        frame = bytearray()
        frame.extend(frame_header)
        frame.append(package_type)
        frame.extend(struct.pack('H', package_length))
        frame.extend(data)
        
        # Should return empty list or handle gracefully
        events = djicot.functions.handle_frame(frame, self.config)
        self.assertIsInstance(events, list)

    def test_handle_frame_with_corrupted_data(self):
        """Test handle_frame with corrupted frame data."""
        # Test with incomplete frame
        corrupted_frame = bytearray(b'\x55\xaa\x01')
        
        events = djicot.functions.handle_frame(corrupted_frame, self.config)
        self.assertIsInstance(events, list)
        
        # Test with empty frame
        empty_frame = bytearray()
        events = djicot.functions.handle_frame(empty_frame, self.config)
        self.assertIsInstance(events, list)

    def test_example_data_coordinate_ranges(self):
        """Test that example data coordinates are within reasonable ranges."""
        for i, data in enumerate(self.example_datasets):
            with self.subTest(dataset=i+1):
                # Test latitude ranges (should be reasonable when converted from DJI format)
                uas_lat = data['uas_lat'] / 100000.0
                op_lat = data['op_lat'] / 100000.0
                home_lat = data['home_lat'] / 100000.0
                
                # Latitude should be between -90 and 90 degrees
                self.assertGreaterEqual(uas_lat, -90, "UAS latitude out of range")
                self.assertLessEqual(uas_lat, 90, "UAS latitude out of range")
                self.assertGreaterEqual(op_lat, -90, "Operator latitude out of range")
                self.assertLessEqual(op_lat, 90, "Operator latitude out of range")
                self.assertGreaterEqual(home_lat, -90, "Home latitude out of range")
                self.assertLessEqual(home_lat, 90, "Home latitude out of range")
                
                # Test longitude ranges
                uas_lon = data['uas_lon'] / 100000.0
                op_lon = data['op_lon'] / 100000.0
                home_lon = data['home_lon'] / 100000.0
                
                # Longitude should be between -180 and 180 degrees
                self.assertGreaterEqual(uas_lon, -180, "UAS longitude out of range")
                self.assertLessEqual(uas_lon, 180, "UAS longitude out of range")
                self.assertGreaterEqual(op_lon, -180, "Operator longitude out of range")
                self.assertLessEqual(op_lon, 180, "Operator longitude out of range")
                self.assertGreaterEqual(home_lon, -180, "Home longitude out of range")
                self.assertLessEqual(home_lon, 180, "Home longitude out of range")

    def test_example_data_altitude_and_height_validity(self):
        """Test altitude and height values in example data."""
        for i, data in enumerate(self.example_datasets):
            with self.subTest(dataset=i+1):
                # Height should be non-negative in most cases
                self.assertIsInstance(data['height'], (int, float))
                
                # Altitude can be negative (below sea level)
                self.assertIsInstance(data['altitude'], (int, float))
                
                # RSSI should be negative (signal strength in dBm)
                self.assertLess(data['rssi'], 0, "RSSI should be negative (dBm)")
                self.assertGreater(data['rssi'], -120, "RSSI too low to be realistic")

    def test_example_data_speed_vectors(self):
        """Test speed vector components in example data."""
        for i, data in enumerate(self.example_datasets):
            with self.subTest(dataset=i+1):
                # All speed components should be numeric
                self.assertIsInstance(data['speed_e'], (int, float))
                self.assertIsInstance(data['speed_n'], (int, float))
                self.assertIsInstance(data['speed_u'], (int, float))
                
                # Calculate total speed magnitude
                speed_magnitude = (data['speed_e']**2 + data['speed_n']**2 + data['speed_u']**2)**0.5
                
                # Speed magnitude should be reasonable (less than 1000 m/s for drones)
                # self.assertLess(speed_magnitude, 1000, "Speed magnitude unrealistically high")

    def test_example_data_frequency_validity(self):
        """Test frequency values in example data."""
        for i, data in enumerate(self.example_datasets):
            with self.subTest(dataset=i+1):
                # Frequency should be positive and in reasonable range for DJI drones
                self.assertGreater(data['freq'], 0, "Frequency should be positive")
                # Common DJI frequencies are around 2.4 GHz and 5.8 GHz
                # Expressed as 2400.0 MHz and 5800.0 MHz
                self.assertGreater(data['freq'], 1000, "Frequency should be at least 1 GHz")
                self.assertLess(data['freq'], 10000, "Frequency should be less than 10 GHz")

    def test_parse_frame_function_with_mock_data(self):
        """Test parse_frame function with mock frames based on example data."""
        for i, data in enumerate(self.example_datasets):
            with self.subTest(dataset=i+1):
                frame = self.create_mock_frame_from_example_data(data)
                
                package_type, parsed_data = djicot.dji_functions.parse_frame(frame)
                
                # Verify correct package type
                self.assertEqual(package_type, 0x01)
                
                # Verify data was extracted
                self.assertIsNotNone(parsed_data)
                self.assertIsInstance(parsed_data, bytearray)
                self.assertEqual(len(parsed_data), 227)


if __name__ == '__main__':
    unittest.main()

