#!/usr/bin/env python3
"""
Test XML validity of output files
"""
import xml.etree.ElementTree as ET
import os
import sys

def test_xml_file(filepath):
    """Test if an XML file is valid"""
    try:
        tree = ET.parse(filepath)
        print(f"✅ {os.path.basename(filepath)}: Valid XML")
        return True
    except ET.ParseError as e:
        print(f"❌ {os.path.basename(filepath)}: Invalid XML - {e}")
        return False
    except Exception as e:
        print(f"❌ {os.path.basename(filepath)}: Error - {e}")
        return False

def main():
    output_dir = "output-xml"
    if not os.path.exists(output_dir):
        print(f"Output directory {output_dir} not found")
        return
    
    files = [f for f in os.listdir(output_dir) if f.endswith('.musicxml')]
    if not files:
        print("No MusicXML files found in output directory")
        return
    
    print(f"Testing {len(files)} MusicXML files for validity...")
    print("=" * 50)
    
    valid_count = 0
    for filename in sorted(files):
        filepath = os.path.join(output_dir, filename)
        if test_xml_file(filepath):
            valid_count += 1
    
    print("=" * 50)
    print(f"Result: {valid_count}/{len(files)} files are valid XML")
    
    if valid_count == len(files):
        print("🎉 All files passed XML validation!")
    else:
        print("⚠️ Some files have XML validation issues")

if __name__ == "__main__":
    main()