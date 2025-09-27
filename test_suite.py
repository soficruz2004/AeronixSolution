import unittest
import os
import tempfile
from unittest.mock import patch, MagicMock
from parser_but_better import BOMParser, CoordinateParser, parse_inputs, detect_file_type
from AI_model import TestGenerator

class TestBOMParser(unittest.TestCase):
    def setUp(self):
        self.parser = BOMParser()
    
    def test_csv_parsing(self):
        csv_content = "Designator,Part Number,Footprint,Quantity,Description\nR1,10K,0603,1,Resistor\nC1,100nF,0603,1,Capacitor"
        components = self.parser._parse_csv_bom(csv_content)
        self.assertEqual(len(components), 2)
        self.assertEqual(components[0].designator, "R1")
        self.assertEqual(components[0].part_number, "10K")
    
    def test_text_parsing(self):
        text_content = "R1 10K 0603 1 Resistor\nC1 100nF 0603 1 Capacitor"
        components = self.parser._parse_text_bom(text_content)
        self.assertEqual(len(components), 2)
        self.assertEqual(components[1].designator, "C1")
    
    def test_priority_assessment(self):
        priority = self.parser._assess_component_priority("U1", "MCU_STM32")
        self.assertEqual(priority, "HIGH")
        
        priority = self.parser._assess_component_priority("R1", "10K")
        self.assertEqual(priority, "MEDIUM")

class TestCoordinateParser(unittest.TestCase):
    def setUp(self):
        self.parser = CoordinateParser()
    
    def test_assembly_testpoint_parsing(self):
        content = "TP1 VCC 10.5 20.3 0\nTP2 GND 15.2 25.1 90"
        test_points = self.parser._parse_assembly_testpoint_report(content)
        self.assertEqual(len(test_points), 2)
        self.assertEqual(test_points[0].net_name, "VCC")
        self.assertEqual(test_points[0].x_coord, 10.5)
    
    def test_xy_coordinate_extraction(self):
        line = "Component at X=12.5 Y=34.7"
        coords = self.parser._extract_xy_coordinates(line)
        match coords:
            case None:
                self.fail("Coordinates should not be None")
            case _:
                self.assertEqual(coords['x'], 12.5)
                self.assertEqual(coords['y'], 34.7)

class TestFileTypeDetection(unittest.TestCase):
    def test_altium_detection(self):
        self.assertEqual(detect_file_type("test.bomdoc"), "ALTIUM_BOM")
        self.assertEqual(detect_file_type("test.schdoc"), "ALTIUM_SCHEMATIC")
    
    def test_standard_detection(self):
        self.assertEqual(detect_file_type("test.csv"), "BOM")
        self.assertEqual(detect_file_type("test.xlsx"), "EXCEL_BOM")
        self.assertEqual(detect_file_type("requirements.txt"), "REQUIREMENTS")

class TestAIModel(unittest.TestCase):
    @patch('AI_model.TestGenerator.generate_resp')
    def test_lora_test_generation(self, mock_resp):
        mock_resp.return_value = "Test procedure generated"
        result = TestGenerator.get_LORA_test([], [], {})
        self.assertEqual(result, "Test procedure generated")
        mock_resp.assert_called_once()
    
    @patch('AI_model.TestGenerator.generate_resp')
    def test_arduino_test_generation(self, mock_resp):
        mock_resp.return_value = "Arduino test generated"
        result = TestGenerator.get_arduino_test([], [])
        self.assertEqual(result, "Arduino test generated")
        mock_resp.assert_called_once()

class TestParseInputs(unittest.TestCase):
    def test_empty_files(self):
        result = parse_inputs([])
        self.assertEqual(len(result['bom_components']), 0)
        self.assertEqual(len(result['test_points']), 0)
    
    def test_csv_file_parsing(self):
        files = [{
            'path': 'test.csv',
            'content': 'Designator,Part Number\nR1,10K\nC1,100nF',
            'type': 'TEXT'
        }]
        result = parse_inputs(files)
        self.assertGreater(len(result['bom_components']), 0)

class TestIntegration(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
    
    def test_end_to_end_workflow(self):
        # Create test CSV file
        csv_file = os.path.join(self.temp_dir, "test_bom.csv")
        with open(csv_file, 'w') as f:
            f.write("Designator,Part Number,Footprint,Quantity,Description\n")
            f.write("U1,STM32F103,LQFP64,1,Microcontroller\n")
            f.write("R1,10K,0603,1,Resistor\n")
        
        # Test file parsing
        files = [{
            'path': csv_file,
            'content': open(csv_file).read(),
            'type': 'TEXT'
        }]
        
        result = parse_inputs(files)
        self.assertEqual(len(result['bom_components']), 2)
        self.assertEqual(result['bom_components'][0].designator, "U1")

class TestExpectedOutput(unittest.TestCase):
    def setUp(self):
        self.expected_output_path = "UF_Hackathon/Example_Output_Files/AE304196-001_LoRa Car Radio Bring-Up Procedure.docx"
        self.input_files_path = "UF_Hackathon/Example_Input_Files"
    
    def test_against_expected_output(self):
        if not os.path.exists(self.expected_output_path):
            self.skipTest("Expected output file not found")
        input_files = self._load_hackathon_input_files()
        if not input_files:
            self.skipTest("No input files found")
        parsed_data = parse_inputs(input_files)
        
        self.assertIn('bom_components', parsed_data)
        self.assertIn('test_points', parsed_data)
        self.assertIn('metadata', parsed_data)
        
        bom_components = parsed_data.get('bom_components', [])
        lora_components = [c for c in bom_components if hasattr(c, 'part_number') and 'LORA' in str(c.part_number).upper()]
        
        with patch('AI_model.TestGenerator.generate_resp') as mock_resp:
            mock_resp.return_value = self._get_mock_lora_test()
            result = TestGenerator.get_LORA_test(bom_components, parsed_data.get('test_points', []), {})
        
        self.assertIsNotNone(result)
        match result:
            case None:
                self.fail("Expected output not generated")
            case _:
                self.assertIn('Power', result)
                self.assertIn('RF', result)
                self.assertIn('LoRa', result)
    
    def _load_hackathon_input_files(self):
        files = []
        if not os.path.exists(self.input_files_path):
            return files
        
        for root, dirs, filenames in os.walk(self.input_files_path):
            for filename in filenames:
                file_path = os.path.join(root, filename)
                file_ext = os.path.splitext(filename)[1].lower()
                
                try:
                    if file_ext in ['.csv', '.txt', '.ipc']:
                        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                            content = f.read()
                        files.append({
                            'path': file_path,
                            'content': content,
                            'type': 'TEXT'
                        })
                    elif file_ext in ['.bomdoc', '.schdoc', '.pcbdoc', '.prjpcb']:
                        files.append({
                            'path': file_path,
                            'content': f"ALTIUM_FILE:{file_ext}",
                            'type': 'ALTIUM_BINARY'
                        })
                except Exception as e:
                    print(f"Error reading {file_path}: {e}")
        
        return files
    
    def _get_mock_lora_test(self):
        """Mock LoRa test output matching expected format"""
        return """1. Title: Power Supply Validation
2. Type: Power
3. Description: Verify 3.3V and 5V rails within tolerance
4. Expected: 3.3V ±5%, 5V ±5%
5. Equipment: Digital multimeter
6. Points: VCC, GND

1. Title: LoRa RF Performance Test
2. Type: RF
3. Description: Measure LoRa sensitivity and range
4. Expected: -137dBm sensitivity @ SF12
5. Equipment: Vector network analyzer, RF generator
6. Points: ANT1, RF_OUT

1. Title: CAN Bus Communication
2. Type: Digital
3. Description: Verify CAN bus functionality
4. Expected: 250kbps data rate, proper framing
5. Equipment: CAN analyzer, oscilloscope
6. Points: CAN_H, CAN_L"""

if __name__ == '__main__':
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    suite.addTests(loader.loadTestsFromTestCase(TestBOMParser))
    suite.addTests(loader.loadTestsFromTestCase(TestCoordinateParser))
    suite.addTests(loader.loadTestsFromTestCase(TestFileTypeDetection))
    suite.addTests(loader.loadTestsFromTestCase(TestAIModel))
    suite.addTests(loader.loadTestsFromTestCase(TestParseInputs))
    suite.addTests(loader.loadTestsFromTestCase(TestIntegration))
    suite.addTests(loader.loadTestsFromTestCase(TestExpectedOutput))
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    print(f"\nTests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    
    if result.wasSuccessful():
        print("✅ All tests passed!")
    else:
        print("❌ Some tests failed")