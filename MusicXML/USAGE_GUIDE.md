# MusicXML Simplifier - Usage Guide

## Quick Start

```bash
# Basic usage
python musicxml_simplifier.py input.musicxml output.musicxml

# With verbose output
python musicxml_simplifier.py input.musicxml output.musicxml --verbose

# Specify rule set (currently only 'downbeat' available)
python musicxml_simplifier.py input.musicxml output.musicxml --rules downbeat
```

## Examples

### Convert Last Christmas trumpet part for beginners:
```bash
python musicxml_simplifier.py "Last Christmas Part 3 Trumpet.musicxml" "Last Christmas Part 3 Trumpet-Simple.musicxml"
```

### Fix rehearsal marks to match measure numbers:
```bash
python musicxml_simplifier.py input.musicxml output.musicxml --rehearsal measure_numbers
```

### Convert rehearsal marks to letters:
```bash
python musicxml_simplifier.py input.musicxml output.musicxml --rehearsal letters
```

### Process extracted MusicXML from compressed file:
```bash
# First extract .mxl file:
copy "file.mxl" "temp.zip"
expand-archive "temp.zip" "extracted"

# Then simplify:
python musicxml_simplifier.py "extracted\score.xml" "simplified.musicxml"
```

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