#!/usr/bin/env python3
"""Test runner script for Aeronix Test Generator"""

import sys
import os
import unittest
import tempfile
from test_data import *

def create_test_files():
    """Create temporary test files"""
    temp_dir = tempfile.mkdtemp()
    
    # Create BOM CSV file
    bom_file = os.path.join(temp_dir, "test_bom.csv")
    with open(bom_file, 'w') as f:
        f.write(SAMPLE_BOM_CSV)
    
    # Create test points file
    tp_file = os.path.join(temp_dir, "test_points.txt")
    with open(tp_file, 'w') as f:
        f.write(SAMPLE_TESTPOINTS)
    
    # Create requirements file
    req_file = os.path.join(temp_dir, "requirements.txt")
    with open(req_file, 'w') as f:
        f.write(SAMPLE_REQUIREMENTS)
    
    return temp_dir, {
        'bom': bom_file,
        'testpoints': tp_file,
        'requirements': req_file
    }

def run_quick_test():
    """Run a quick functionality test"""
    print("🚀 Running Quick Functionality Test...")
    
    try:
        # Test parser import
        from parser_but_better import BOMParser, parse_inputs
        print("✅ Parser import successful")
        
        # Test AI model import
        from AI_model import TestGenerator
        print("✅ AI model import successful")
        
        # Test basic parsing
        parser = BOMParser()
        components = parser._parse_csv_bom(SAMPLE_BOM_CSV)
        print(f"✅ Parsed {len(components)} components")
        
        # Test file type detection
        from parser_but_better import detect_file_type
        file_type = detect_file_type("test.csv")
        print(f"✅ File type detection: {file_type}")
        
        print("🎉 Quick test passed!")
        return True
        
    except Exception as e:
        print(f"❌ Quick test failed: {e}")
        return False

def run_full_tests():
    """Run the full test suite"""
    print("🧪 Running Full Test Suite...")
    
    # Import and run test suite
    from test_suite import *
    
    # Create test runner
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add all test classes
    test_classes = [
        TestBOMParser,
        TestCoordinateParser, 
        TestFileTypeDetection,
        TestAIModel,
        TestParseInputs,
        TestIntegration
    ]
    
    for test_class in test_classes:
        suite.addTests(loader.loadTestsFromTestCase(test_class))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result.wasSuccessful()

def test_with_real_files():
    """Test with actual project files if available"""
    print("📁 Testing with real files...")
    
    test_files_dir = "UF_Hackathon/Example_Input_Files"
    if os.path.exists(test_files_dir):
        print(f"✅ Found test files directory: {test_files_dir}")
        
        # Look for actual files
        for root, dirs, files in os.walk(test_files_dir):
            for file in files:
                if file.endswith(('.csv', '.txt', '.BomDoc', '.SchDoc')):
                    print(f"📄 Found: {file}")
    else:
        print("⚠️  No real test files found")

def main():
    """Main test runner"""
    print("=" * 50)
    print("🔧 AERONIX TEST GENERATOR - TEST SUITE")
    print("=" * 50)
    
    # Run quick test first
    if not run_quick_test():
        print("❌ Quick test failed - stopping")
        sys.exit(1)
    
    print("\n" + "-" * 30)
    
    # Run full test suite
    if run_full_tests():
        print("🎉 All tests passed!")
    else:
        print("❌ Some tests failed")
    
    print("\n" + "-" * 30)
    
    # Test with real files
    test_with_real_files()
    
    print("\n" + "=" * 50)
    print("✅ Test run complete!")

if __name__ == "__main__":
    main()