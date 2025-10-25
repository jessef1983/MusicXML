# MusicXML Simplifier - Usage Guide

## Project Structure

```
MusicXML/
├── input-xml/          # Place your original MusicXML files here
├── output-xml/         # Processed files will be saved here
├── musicxml_simplifier.py
├── MUSICXML_SIMPLIFIER_RULES.md
└── USAGE_GUIDE.md
```

## Quick Start

```bash
# Basic usage - input from input-xml folder, output to output-xml folder
python musicxml_simplifier.py input-xml/input.musicxml output-xml/output.musicxml

# With verbose output
python musicxml_simplifier.py input-xml/input.musicxml output-xml/output.musicxml --verbose

# Specify rule set (currently only 'downbeat' available)
python musicxml_simplifier.py input-xml/input.musicxml output-xml/output.musicxml --rules downbeat
```

## Examples

### Convert Last Christmas trumpet part for beginners:
```bash
python musicxml_simplifier.py "input-xml/Last Christmas Part 3 Trumpet.musicxml" "output-xml/Last Christmas Part 3 Trumpet-Simple.musicxml"
```

### Fix rehearsal marks to match measure numbers:
```bash
python musicxml_simplifier.py input-xml/input.musicxml output-xml/output.musicxml --rehearsal measure_numbers
```

### Convert rehearsal marks to letters:
```bash
python musicxml_simplifier.py input-xml/input.musicxml output-xml/output.musicxml --rehearsal letters
```

### Remove multi-measure rests for easier counting:
```bash
python musicxml_simplifier.py input-xml/input.musicxml output-xml/output.musicxml --remove-multimeasure-rests
```

### All beginner-friendly options combined:
```bash
python musicxml_simplifier.py input-xml/input.musicxml output-xml/output.musicxml \
  --sync-part-names "Easy Version" --center-title --remove-multimeasure-rests \
  --rehearsal letters --verbose
```

### Process extracted MusicXML from compressed file:
```bash
# First extract .mxl file from input-xml folder:
copy "input-xml/file.mxl" "temp.zip"
expand-archive "temp.zip" "extracted"

# Then simplify and save to output-xml:
python musicxml_simplifier.py "extracted/score.xml" "output-xml/simplified.musicxml"
```

### Working with the new folder structure:
```bash
# Process all files from input-xml to output-xml
# Example with the provided sample files:
python musicxml_simplifier.py "input-xml/Last Christmas Part 3 Trumpet Original.musicxml" "output-xml/Last Christmas Part 3 Trumpet Original-Simplified.musicxml"
```

## Batch Processing

For processing multiple files at once, use the batch processing helper:

```bash
# Process all files in input-xml folder
python batch_process.py

# Process with custom suffix
python batch_process.py --suffix "Beginner"

# Process with rehearsal mark fixes and verbose output
python batch_process.py --rehearsal letters --verbose --suffix "Easy"

# Preview what would be processed (dry run)
python batch_process.py --dry-run
```

The batch processor will:
- Automatically find all MusicXML files in the `input-xml` folder
- Process each one using your specified settings
- Save results to the `output-xml` folder with appropriate naming
- Provide progress feedback and error reporting

## Rule Sets

### Current: `downbeat` (Default)
- Converts eighth note pairs to quarter notes
- Keeps first note of each pair (downbeat)
- Preserves articulations from first note
- Handles rests appropriately
- Perfect for beginner students

### Future Rule Sets (Planned)
- `triplet`: Handle eighth note triplets
- `syncopation`: Advanced syncopation simplification  
- `conservative`: Minimal changes, preserve more complexity
- `custom`: User-defined rules via config file

## File Requirements

### Supported Input Formats:
- `.musicxml` (uncompressed MusicXML)
- `.xml` (MusicXML format)

### Supported Output:
- Always outputs uncompressed `.musicxml`
- Compatible with MuseScore, Finale, Sibelius
- Can be re-compressed to `.mxl` if needed

## Adding New Rules

1. Edit `MUSICXML_SIMPLIFIER_RULES.md` to document new rules
2. Add new rule method to `MusicXMLSimplifier` class
3. Update `--rules` choices in argument parser
4. Test thoroughly with sample files

## Troubleshooting

### Common Issues:
- **File not found**: Check file path and extension
- **Encoding errors**: Ensure file is UTF-8 encoded
- **Invalid MusicXML**: Validate input file in music software first

### Validation:
Always test output files in MuseScore or your preferred notation software to ensure they load correctly.

## Development

The script is designed to be modular and extensible. Each rule set is implemented as a separate method, making it easy to add new simplification strategies without affecting existing functionality.