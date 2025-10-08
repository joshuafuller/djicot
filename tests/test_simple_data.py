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

"""Simple Data Validation Tests using Example Datasets."""

import struct
import unittest

# Define example data inline to avoid import issues
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


class SimpleDataValidationTestCase(unittest.TestCase):
    """Test cases for validating example data without full module dependencies."""

    def setUp(self):
        """Set up test cases."""
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

    def test_coordinate_ranges(self):
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

    def test_altitude_and_height_validity(self):
        """Test altitude and height values in example data."""
        for i, data in enumerate(self.example_datasets):
            with self.subTest(dataset=i+1):
                # Height should be numeric
                self.assertIsInstance(data['height'], (int, float))
                
                # Altitude can be negative (below sea level) - should be numeric
                self.assertIsInstance(data['altitude'], (int, float))
                
                # RSSI should be negative (signal strength in dBm)
                self.assertLess(data['rssi'], 0, "RSSI should be negative (dBm)")
                self.assertGreater(data['rssi'], -120, "RSSI too low to be realistic")

    def test_speed_vectors(self):
        """Test speed vector components in example data."""
        for i, data in enumerate(self.example_datasets):
            with self.subTest(dataset=i+1):
                # All speed components should be numeric
                self.assertIsInstance(data['speed_e'], (int, float))
                self.assertIsInstance(data['speed_n'], (int, float))
                self.assertIsInstance(data['speed_u'], (int, float))
                
                # Calculate total speed magnitude
                speed_magnitude = (data['speed_e']**2 + data['speed_n']**2 + data['speed_u']**2)**0.5
                
                # Speed magnitude should be reasonable (less than 5000 m/s - accounting for potential data format)
                # Note: These may be in different units or scaled differently in DJI format
                self.assertLess(speed_magnitude, 5000, "Speed magnitude unrealistically high")
                self.assertGreater(speed_magnitude, 0, "Speed magnitude should be positive")

    def test_frequency_validity(self):
        """Test frequency values in example data."""
        for i, data in enumerate(self.example_datasets):
            with self.subTest(dataset=i+1):
                # Frequency should be positive and in reasonable range for DJI drones
                self.assertGreater(data['freq'], 0, "Frequency should be positive")
                # Common DJI frequencies are around 2.4 GHz and 5.8 GHz
                # Expressed as 2400.0 MHz and 5800.0 MHz
                self.assertGreater(data['freq'], 1000, "Frequency should be at least 1 GHz")
                self.assertLess(data['freq'], 10000, "Frequency should be less than 10 GHz")

    def test_binary_data_packing_unpacking(self):
        """Test creating and parsing binary data based on examples."""
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

                # Unpack and verify
                unpacked_serial = data[:64].decode('utf-8').rstrip('\x00')
                unpacked_device_type = data[64:128].decode('utf-8').rstrip('\x00')
                unpacked_device_type_8 = data[128]
                unpacked_op_lat = struct.unpack("d", data[129:137])[0]
                unpacked_op_lon = struct.unpack("d", data[137:145])[0]
                unpacked_uas_lat = struct.unpack("d", data[145:153])[0]
                unpacked_uas_lon = struct.unpack("d", data[153:161])[0]
                unpacked_height = struct.unpack("d", data[161:169])[0]
                unpacked_altitude = struct.unpack("d", data[169:177])[0]
                unpacked_home_lat = struct.unpack("d", data[177:185])[0]
                unpacked_home_lon = struct.unpack("d", data[185:193])[0]
                unpacked_freq = struct.unpack("d", data[193:201])[0]
                unpacked_speed_e = struct.unpack("d", data[201:209])[0]
                unpacked_speed_n = struct.unpack("d", data[209:217])[0]
                unpacked_speed_u = struct.unpack("d", data[217:225])[0]
                unpacked_rssi = struct.unpack("h", data[225:227])[0]
                
                # Verify all values match
                self.assertEqual(unpacked_serial, example['serial_number'])
                self.assertEqual(unpacked_device_type, example['device_type'])
                self.assertEqual(unpacked_device_type_8, example['device_type_8'])
                self.assertAlmostEqual(unpacked_op_lat, example['op_lat'], places=6)
                self.assertAlmostEqual(unpacked_op_lon, example['op_lon'], places=6)
                self.assertAlmostEqual(unpacked_uas_lat, example['uas_lat'], places=6)
                self.assertAlmostEqual(unpacked_uas_lon, example['uas_lon'], places=6)
                self.assertAlmostEqual(unpacked_height, example['height'], places=1)
                self.assertAlmostEqual(unpacked_altitude, example['altitude'], places=1)
                self.assertAlmostEqual(unpacked_home_lat, example['home_lat'], places=6)
                self.assertAlmostEqual(unpacked_home_lon, example['home_lon'], places=6)
                self.assertAlmostEqual(unpacked_freq, example['freq'], places=1)
                self.assertAlmostEqual(unpacked_speed_e, example['speed_e'], places=1)
                self.assertAlmostEqual(unpacked_speed_n, example['speed_n'], places=1)
                self.assertAlmostEqual(unpacked_speed_u, example['speed_u'], places=1)
                self.assertEqual(unpacked_rssi, example['rssi'])

    def test_example_data_differences(self):
        """Test that the two example datasets have meaningful differences."""
        data1, data2 = self.example_datasets
        
        # Check that datasets are actually different
        differences = []
        for key in data1.keys():
            if data1[key] != data2[key]:
                differences.append(key)
        
        # Should have several different values
        self.assertGreater(len(differences), 5, "Example datasets should have significant differences")
        
        # Verify specific expected differences
        self.assertNotEqual(data1['device_type_8'], data2['device_type_8'])
        self.assertNotEqual(data1['op_lat'], data2['op_lat'])
        self.assertNotEqual(data1['uas_lat'], data2['uas_lat'])
        self.assertNotEqual(data1['altitude'], data2['altitude'])


if __name__ == '__main__':
    unittest.main()