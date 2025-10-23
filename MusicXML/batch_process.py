#!/usr/bin/env python3
"""
MusicXML Simplifier - Batch Processing Helper

A helper script to process multiple files from input-xml to output-xml folder.
Useful for batch processing and maintaining organized project structure.

Author: GitHub Copilot
Date: 2025-10-23
"""

import os
import sys
from pathlib import Path
import subprocess
import argparse


def get_input_files():
    """Get all MusicXML files from the input-xml directory."""
    input_dir = Path("input-xml")
    if not input_dir.exists():
        print("❌ input-xml directory not found!")
        return []
    
    patterns = ["*.musicxml", "*.xml", "*.mxl"]
    files = []
    for pattern in patterns:
        files.extend(input_dir.glob(pattern))
    
    return sorted(files)


def create_output_filename(input_path, suffix="Simplified"):
    """Create an output filename based on input filename."""
    stem = input_path.stem
    extension = ".musicxml"  # Always output as .musicxml
    
    # If file already has a suffix, replace it
    if any(word in stem for word in ["Original", "Test"]):
        output_name = f"{stem}-{suffix}{extension}"
    else:
        output_name = f"{stem}-{suffix}{extension}"
    
    return Path("output-xml") / output_name


def process_file(input_path, output_path, args):
    """Process a single file using the musicxml_simplifier."""
    cmd = [
        sys.executable, "musicxml_simplifier.py",
        str(input_path), str(output_path)
    ]
    
    if args.rules:
        cmd.extend(["--rules", args.rules])
    if args.rehearsal and args.rehearsal != "none":
        cmd.extend(["--rehearsal", args.rehearsal])
    if args.verbose:
        cmd.append("--verbose")
    if args.center_title:
        cmd.append("--center-title")
    if args.sync_part_names:
        cmd.extend(["--sync-part-names", args.sync_part_names])
    if args.no_clean_credits:
        cmd.append("--no-clean-credits")
    if args.remove_multimeasure_rests:
        cmd.append("--remove-multimeasure-rests")
    
    print(f"🔄 Processing: {input_path.name}")
    print(f"   → Output: {output_path.name}")
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"   ✅ Success!")
            return True
        else:
            print(f"   ❌ Failed: {result.stderr}")
            return False
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(description="Batch process MusicXML files from input-xml to output-xml")
    parser.add_argument('--rules', default='downbeat', choices=['downbeat'],
                       help='Simplification rule set to apply')
    parser.add_argument('--rehearsal', default='none', 
                       choices=['none', 'measure_numbers', 'letters'],
                       help='Rehearsal mark processing mode')
    parser.add_argument('--suffix', default='Simplified',
                       help='Suffix to add to output filenames (default: Simplified)')
    parser.add_argument('--verbose', '-v', action='store_true',
                       help='Show detailed processing information')
    parser.add_argument('--center-title', action='store_true',
                       help='Center the title text')
    parser.add_argument('--sync-part-names', type=str,
                       help='Sync all part names to this value')
    parser.add_argument('--no-clean-credits', action='store_true',
                       help='Skip cleaning up multi-line credit text')
    parser.add_argument('--remove-multimeasure-rests', action='store_true',
                       help='Convert multi-measure rests into individual measure rests')
    parser.add_argument('--dry-run', action='store_true',
                       help='Show what would be processed without actually doing it')
    
    args = parser.parse_args()
    
    # Ensure output directory exists
    output_dir = Path("output-xml")
    output_dir.mkdir(exist_ok=True)
    
    # Get input files
    input_files = get_input_files()
    if not input_files:
        print("❌ No MusicXML files found in input-xml directory!")
        return
    
    print(f"🎵 Found {len(input_files)} input file(s):")
    for file in input_files:
        print(f"   • {file.name}")
    print()
    
    if args.dry_run:
        print("🧪 DRY RUN - showing what would be processed:")
        for input_path in input_files:
            output_path = create_output_filename(input_path, args.suffix)
            print(f"   {input_path} → {output_path}")
        return
    
    # Process files
    success_count = 0
    total_count = len(input_files)
    
    for input_path in input_files:
        output_path = create_output_filename(input_path, args.suffix)
        
        if process_file(input_path, output_path, args):
            success_count += 1
        print()  # Empty line between files
    
    # Summary
    print(f"📊 Processing complete!")
    print(f"   ✅ Successful: {success_count}/{total_count}")
    if success_count < total_count:
        print(f"   ❌ Failed: {total_count - success_count}")
    
    if success_count > 0:
        print(f"\n🎉 Check the output-xml folder for your simplified files!")


if __name__ == '__main__':
    main()