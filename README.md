# MusicXML Simplifier

A Python tool for simplifying complex rhythms in MusicXML files to make them more accessible for beginner musicians.

## 🎵 What it does

The MusicXML Simplifier converts complex eighth note patterns to simpler quarter note patterns using the "downbeat trumps upbeat" principle. This makes sheet music much easier for beginning students to read and play.

## 📁 Project Structure

```
MusicXML/
├── input-xml/                    # 📥 Original MusicXML files
│   ├── Last Christmas Part 3 Trumpet Original.musicxml
│   ├── Last Christmas Part 3 Trumpet.musicxml
│   ├── Last Christmas Part 3 Trumpet Part Name Test.musicxml
│   └── Last Christmas Part 3 Trumpet-Part_3_Trumpet.mxl
├── output-xml/                   # 📤 Processed/simplified files
│   ├── Last Christmas Part 3 Trumpet - FINAL PRODUCTION.musicxml
│   ├── Last Christmas Part 3 Trumpet-Simple.musicxml
│   ├── Last Christmas Part 3 Trumpet-Beginner.musicxml
│   └── ... (14 processed variations)
├── musicxml_simplifier.py        # 🚀 Main application
├── batch_process.py             # 🔄 Batch processing helper
├── MUSICXML_SIMPLIFIER_RULES.md  # 📋 Detailed rules documentation
├── USAGE_GUIDE.md               # 📖 Usage instructions and examples
└── README.md                    # 📄 This file
```

## 🚀 Quick Start

### Single File Processing
```bash
# Basic usage (rhythm simplification for beginners)
python musicxml_simplifier.py input-xml/your-file.musicxml output-xml/simplified-file.musicxml

# With all beginner-friendly options enabled
python musicxml_simplifier.py input-xml/your-file.musicxml output-xml/simplified-file.musicxml \
  --sync-part-names "Easy Trumpet" --center-title --remove-multimeasure-rests --verbose

# OMR correction only (preserve original rhythms, fix PDF conversion issues)
python musicxml_simplifier.py input-xml/your-file.musicxml output-xml/corrected-file.musicxml \
  --skip-rhythm-simplification --center-title --verbose
```

### Batch Processing (Process all files in input-xml folder)
```bash
# Process all files with default settings (includes rhythm simplification, 
# rehearsal mark validation, title centering, multi-measure rest removal, 
# auto-sync part names for consistency, and verbose output)
python batch_process.py

# Process with custom options
python batch_process.py --suffix "Easy" --rehearsal letters \
  --sync-part-names "Beginner Version" --quiet

# OMR correction mode (fix PDF conversion issues without changing rhythms)
python batch_process.py --skip-rhythm-simplification --suffix "Corrected"

# Minimal processing (rhythm only)
python batch_process.py --rehearsal none --no-center-title \
  --keep-multimeasure-rests --quiet

# See what would be processed without actually doing it
python batch_process.py --dry-run
```

## 📋 Features

### 🎼 Rhythm Simplification (Default Mode)
- **Rhythm Simplification**: Converts eighth note pairs to quarter notes
- **Downbeat Priority**: Always keeps the first note of each pair
- **Smart Rest Handling**: Handles rest combinations intelligently
- **High Note Transposition**: Moves challenging notes to beginner-friendly octaves

### 🔧 OMR Correction Mode (`--skip-rhythm-simplification`)
- **Original Rhythm Preservation**: Maintains all original note values and pitches
- **Instrument Metadata Correction**: Fixes wrong transpositions, sounds, MIDI programs
- **Title Generation**: Adds missing titles from filename
- **Credit Text Cleanup**: Fixes problematic characters that cause truncation in MuseScore
- **Part Name Synchronization**: Updates part names consistently across all references

### 🎵 Common Features (Both Modes)
- **Articulation Preservation**: Maintains important musical markings
- **Rehearsal Mark Management**: Fix and convert rehearsal marks
- **Multi-measure Rest Removal**: Converts multi-measure rests to individual rests for easier counting
- **Organized File Structure**: Separate input and output folders for better organization

## 📖 Documentation

- **[USAGE_GUIDE.md](USAGE_GUIDE.md)**: Comprehensive usage instructions with examples
- **[MUSICXML_SIMPLIFIER_RULES.md](MUSICXML_SIMPLIFIER_RULES.md)**: Detailed explanation of simplification rules

## 🎯 Use Cases

### Rhythm Simplification Mode (Default)
- **Music Education**: Simplify complex pieces for beginning students
- **Reading Practice**: Make sight-reading exercises more accessible

### OMR Correction Mode (`--skip-rhythm-simplification`)
- **PDF Conversion Cleanup**: Fix issues from optical music recognition (OMR) software
- **Metadata Correction**: Correct instrument assignments and transpositions after scanning
- **Professional Engraving**: Clean up files while preserving original composer intent
- **Sight-Reading Practice**: Create easier versions for skill development
- **Ensemble Preparation**: Generate practice parts at different difficulty levels
- **Music Therapy**: Adapt pieces for different ability levels

## 🔧 Requirements

- Python 3.6+
- Input files in MusicXML (.musicxml, .xml) or compressed MusicXML (.mxl) format
- Compatible with MuseScore, Finale, Sibelius, and other notation software

## 🎼 Example

**Before (Eighth Notes):**
```
♪ ♪ ♪ ♪ | ♪ ♪ ♪ ♪
C D E F   G A B C
```

**After (Quarter Notes):**
```
♩   ♩   | ♩   ♩
C   E     G   B
```

## 🤝 Contributing

This project is designed to be modular and extensible. You can:

1. Add new rule sets in the `MusicXMLSimplifier` class
2. Update documentation for new features
3. Add sample files to test new functionality
4. Improve the file organization and workflow

---

**Created by:** GitHub Copilot  
**Date:** October 23, 2025