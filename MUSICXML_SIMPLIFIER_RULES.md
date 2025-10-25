# MusicXML Rhythm Simplifier

This script simplifies MusicXML files by converting complex eighth note patterns to quarter notes, making them easier for beginner musicians to read and play.

## Current Rules (Downbeat Simplification)

The script applies the "downbeat trumps upbeat" principle with these specific rules:

### 1. **Pair Processing**
- Process eighth notes in pairs (2 eighth notes = 1 beat)
- Always keep the **first note** of each pair (the downbeat)
- Discard the second note of each pair (the upbeat)

### 2. **Note Conversion**
- Convert each eighth note pair → single quarter note
- **Duration**: Change from `duration=1` to `duration=2`
- **Type**: Change from `<type>eighth</type>` to `<type>quarter</type>`

### 3. **Pitch Selection**
- **Always use the first note's pitch** in each pair
- Example: Eighth C + Eighth D → Quarter C

### 4. **Rest Handling**
- **If rest is first**: Convert entire pair to quarter rest (note gets "swallowed")
- **If note is first**: Convert pair to quarter note (ignore any following rest)
- Example: Eighth rest + Eighth C → Quarter rest (C disappears)
- Example: Eighth C + Eighth rest → Quarter C

### 5. **Articulation Preservation**
- **Keep all articulations** from the first note in each pair
- Remove articulations from discarded notes
- Example: Accent on first eighth → Accent on resulting quarter

### 6. **Beam Removal**
- Remove all `<beam>` elements since quarter notes don't beam
- Clean up `begin`, `continue`, `end` beam markers

### 7. **Measure Integrity**
- Maintain exactly 4 beats per 4/4 measure
- Ensure total duration always equals time signature requirements

## Usage Examples

### Basic rhythm simplification:
```bash
python musicxml_simplifier.py input.musicxml output.musicxml
```

### With rehearsal mark fixing:
```bash
python musicxml_simplifier.py input.musicxml output.musicxml --rehearsal measure_numbers
```

### With title centering:
```bash
python musicxml_simplifier.py input.musicxml output.musicxml --center-title
```

### With part name synchronization:
```bash
python musicxml_simplifier.py input.musicxml output.musicxml --sync-part-names "Part 3 Trumpet Easy"
```

### Full processing (all features):
```bash
python musicxml_simplifier.py input.musicxml output.musicxml --rehearsal letters --center-title --sync-part-names "Part 3 Trumpet Easy"
```

## Additional Features

### Rehearsal Mark Correction
- **Fix incorrect marks**: Corrects rehearsal marks that don't match measure numbers
- **Two modes**: 
  - `measure_numbers`: Fix marks to match actual measure numbers
  - `letters`: Convert to sequential A, B, C, D format
- **Example**: Measure 35 showing "58" gets corrected to "35"

### Title Centering
- **Center main title**: Automatically centers the main title on the page
- **Smart detection**: Finds title by large font size (20+ points)
- **Page-aware**: Calculates center position based on actual page width
- **Usage**: `--center-title` flag

### Part Name Synchronization
- **Unified part names**: Updates all part name references throughout the file
- **Multiple locations**: Syncs header metadata, visual credits, and part definitions
- **Custom naming**: Specify any name (e.g., "Part 3 Trumpet Easy", "Beginner Trumpet")
- **Smart detection**: Automatically finds and updates part name references
- **Usage**: `--sync-part-names "New Part Name"`

## Future Rule Extensions

### Possible Additional Rules:
- **Triplet handling**: How to simplify eighth note triplets
- **Syncopation**: Options for handling syncopated patterns
- **Different time signatures**: Rules for 3/4, 2/4, etc.
- **Mixed note values**: Handling when quarters and eighths are mixed
- **Grace note handling**: Whether to preserve or remove grace notes
- **Tie simplification**: How to handle tied notes across beats

### Custom Rule Templates:
```markdown
### Rule Name: [Description]
- **When**: [Condition]
- **Action**: [What to do]
- **Preserve**: [What to keep]
- **Example**: [Before] → [After]
```

## Usage

```bash
python musicxml_simplifier.py input_file.musicxml output_file.musicxml --rules downbeat --rehearsal measure_numbers
```

### Rehearsal Mark Options:
- `--rehearsal measure_numbers`: Fix marks to match measure numbers (default)
- `--rehearsal letters`: Convert to sequential letters (A, B, C, D...)  
- `--rehearsal none`: Don't modify rehearsal marks

## Supported Formats
- Uncompressed MusicXML (.musicxml, .xml)
- Input: Any valid MusicXML file
- Output: Simplified MusicXML file compatible with MuseScore and other notation software