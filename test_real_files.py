#!/usr/bin/env python3
"""Test with real hackathon files"""

import os
import sys
from parser_but_better import parse_inputs
from AI_model import TestGenerator
from format_output import format_test_output

def find_hackathon_files():
    """Find all hackathon input files"""
    base_path = "UF_Hackathon/Example_Input_Files"
    files = []
    
    if not os.path.exists(base_path):
        print(f"❌ Hackathon files not found at: {base_path}")
        return files
    
    print(f"🔍 Searching for files in: {base_path}")
    
    for root, dirs, filenames in os.walk(base_path):
        for filename in filenames:
            file_path = os.path.join(root, filename)
            file_ext = os.path.splitext(filename)[1].lower()
            
            print(f"📄 Found: {filename}")
            
            try:
                if file_ext in ['.csv', '.txt', '.ipc', '.md']:
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
                elif file_ext in ['.pdf', '.docx']:
                    files.append({
                        'path': file_path,
                        'content': f"DOCUMENT_FILE:{file_ext}",
                        'type': 'DOCUMENT'
                    })
            except Exception as e:
                print(f"⚠️  Error reading {filename}: {e}")
    
    print(f"✅ Found {len(files)} processable files")
    return files

def test_parsing():
    """Test parsing with real files"""
    print("\n" + "="*50)
    print("🔧 TESTING WITH REAL HACKATHON FILES")
    print("="*50)
    
    # Find files
    files = find_hackathon_files()
    if not files:
        print("❌ No files to process")
        return None
    
    # Parse files
    print("\n📊 Parsing files...")
    try:
        parsed_data = parse_inputs(files)
        
        # Show results
        bom_count = len(parsed_data.get('bom_components', []))
        tp_count = len(parsed_data.get('test_points', []))
        
        print(f"✅ Parsed {bom_count} BOM components")
        print(f"✅ Parsed {tp_count} test points")
        
        # Show component details
        if bom_count > 0:
            print("\n📋 Sample Components:")
            for i, comp in enumerate(parsed_data['bom_components'][:5]):
                if hasattr(comp, 'designator'):
                    print(f"  {comp.designator}: {comp.part_number} ({comp.test_priority})")
                else:
                    print(f"  Component {i}: {comp}")
        
        # Show test points
        if tp_count > 0:
            print("\n📍 Sample Test Points:")
            for i, tp in enumerate(parsed_data['test_points'][:3]):
                if hasattr(tp, 'net_name'):
                    print(f"  {tp.component_ref}: {tp.net_name} @ ({tp.x_coord}, {tp.y_coord})")
                else:
                    print(f"  Test Point {i}: {tp}")
        
        return parsed_data
        
    except Exception as e:
        print(f"❌ Parsing failed: {e}")
        return None

def test_ai_generation(parsed_data):
    """Test AI generation with real data"""
    if not parsed_data:
        return None
    
    print("\n🤖 Testing AI Generation...")
    
    try:
        bom_components = parsed_data.get('bom_components', [])
        test_points = parsed_data.get('test_points', [])
        requirements = parsed_data.get('requirements', {})
        
        # Generate LoRa test
        print("🔄 Generating LoRa test...")
        lora_test = TestGenerator.get_LORA_test(bom_components, test_points, requirements)
        
        if lora_test:
            print("✅ LoRa test generated successfully")
            print(f"📝 Length: {len(lora_test)} characters")
            return lora_test
        else:
            print("❌ LoRa test generation failed")
            return None
            
    except Exception as e:
        print(f"❌ AI generation failed: {e}")
        return None

def test_output_formatting(test_data):
    """Test professional output formatting"""
    if not test_data:
        return None
    
    print("\n📄 Testing Output Formatting...")
    
    try:
        filename = format_test_output(test_data, "LoRa Car Radio")
        print(f"✅ Professional document created: {filename}")
        
        if os.path.exists(filename):
            size = os.path.getsize(filename)
            print(f"📊 File size: {size:,} bytes")
            return filename
        else:
            print("❌ Output file not found")
            return None
            
    except Exception as e:
        print(f"❌ Output formatting failed: {e}")
        return None

def main():
    """Main test function"""
    print("🚀 AERONIX END-TO-END TEST")
    print("Testing with real hackathon files...")
    
    # Test 1: File parsing
    parsed_data = test_parsing()
    
    # Test 2: AI generation
    test_data = test_ai_generation(parsed_data)
    
    # Test 3: Output formatting
    output_file = test_output_formatting(test_data)
    
    # Summary
    print("\n" + "="*50)
    print("📊 TEST SUMMARY")
    print("="*50)
    
    results = {
        "File Parsing": "✅ PASS" if parsed_data else "❌ FAIL",
        "AI Generation": "✅ PASS" if test_data else "❌ FAIL", 
        "Output Formatting": "✅ PASS" if output_file else "❌ FAIL"
    }
    
    for test, result in results.items():
        print(f"{test}: {result}")
    
    if all("✅" in result for result in results.values()):
        print("\n🎉 ALL TESTS PASSED!")
        print(f"📄 Final output: {output_file}")
    else:
        print("\n⚠️  Some tests failed")
    
    return all("✅" in result for result in results.values())

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)