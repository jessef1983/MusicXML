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
# Basic usage
python musicxml_simplifier.py input-xml/your-file.musicxml output-xml/simplified-file.musicxml

# With all beginner-friendly options enabled
python musicxml_simplifier.py input-xml/your-file.musicxml output-xml/simplified-file.musicxml \
  --sync-part-names "Easy Trumpet" --center-title --remove-multimeasure-rests --verbose
```

### Batch Processing (Process all files in input-xml folder)
```bash
# Process all files with default settings (includes rhythm simplification, 
# rehearsal mark validation, title centering, multi-measure rest removal, and verbose output)
python batch_process.py

# Process with custom options
python batch_process.py --suffix "Easy" --rehearsal letters \
  --sync-part-names "Beginner Version" --quiet

# Minimal processing (rhythm only)
python batch_process.py --rehearsal none --no-center-title \
  --keep-multimeasure-rests --quiet

# See what would be processed without actually doing it
python batch_process.py --dry-run
```

## 📋 Features

- **Rhythm Simplification**: Converts eighth note pairs to quarter notes
- **Downbeat Priority**: Always keeps the first note of each pair
- **Smart Rest Handling**: Handles rest combinations intelligently
- **Articulation Preservation**: Maintains important musical markings
- **Rehearsal Mark Management**: Fix and convert rehearsal marks
- **Part Name Synchronization**: Update part names consistently
- **Credit Text Cleanup**: Fixes problematic characters that cause truncation in MuseScore
- **Multi-measure Rest Removal**: Converts multi-measure rests to individual rests for easier counting
- **Organized File Structure**: Separate input and output folders for better organization

## 📖 Documentation

- **[USAGE_GUIDE.md](USAGE_GUIDE.md)**: Comprehensive usage instructions with examples
- **[MUSICXML_SIMPLIFIER_RULES.md](MUSICXML_SIMPLIFIER_RULES.md)**: Detailed explanation of simplification rules

## 🎯 Use Cases

- **Music Education**: Simplify complex pieces for beginning students
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