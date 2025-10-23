#!/usr/bin/env python3
"""
MusicXML Rhythm Simplifier

A tool for simplifying complex rhythms in MusicXML files to make them
more accessible for beginner musicians.

Author: GitHub Copilot
Date: 2025-10-23
"""

import re
import sys
import argparse
from pathlib import Path


class MusicXMLSimplifier:
    """
    Main class for simplifying MusicXML rhythm patterns.
    """
    
    def __init__(self):
        self.rules_applied = []
        self.measures_processed = 0
        self.eighth_notes_converted = 0
        self.rehearsal_marks_fixed = 0
        self.multimeasure_rests_removed = 0
        
    def apply_downbeat_rules(self, content):
        """
        Apply downbeat simplification rules to MusicXML content.
        
        Rules:
        1. Convert eighth note pairs to quarter notes
        2. Keep first note's pitch and articulation
        3. Handle rests appropriately
        4. Remove beam elements
        5. Maintain measure timing
        """
        
        lines = content.split('\n')
        result_lines = []
        i = 0
        
        while i < len(lines):
            line = lines[i]
            
            # Track measures for progress
            if '<measure number=' in line:
                self.measures_processed += 1
                
            # Look for eighth note patterns to convert
            if self._is_eighth_note_start(lines, i):
                # Find the complete note block
                note_block, next_index = self._extract_note_block(lines, i)
                
                # Check if this is part of a pair we should simplify
                if next_index < len(lines):
                    next_block, final_index = self._extract_note_block(lines, next_index)
                    
                    # If we have a pair of eighth notes/rests, simplify them
                    if (self._is_eighth_note_block(note_block) and 
                        (self._is_eighth_note_block(next_block) or self._is_eighth_rest_block(next_block))):
                        
                        # Apply downbeat rule: keep first, convert to quarter
                        simplified_block = self._convert_to_quarter_note(note_block)
                        result_lines.extend(simplified_block)
                        
                        # Skip the second note in the pair
                        i = final_index
                        self.eighth_notes_converted += 2
                        continue
                    
                    # Handle rest + note pairs (rest on downbeat swallows the note)
                    elif (self._is_eighth_rest_block(note_block) and 
                          self._is_eighth_note_block(next_block)):
                        
                        # Convert rest to quarter rest, swallow the note
                        simplified_block = self._convert_to_quarter_rest(note_block)
                        result_lines.extend(simplified_block)
                        
                        # Skip the second note (it gets swallowed)
                        i = final_index
                        self.eighth_notes_converted += 2
                        continue
                
                # If not part of a pair, add as-is but check for single eighth conversion
                result_lines.extend(note_block)
                i = next_index
            else:
                result_lines.append(line)
                i += 1
        
        # Remove beam elements
        result_content = '\n'.join(result_lines)
        result_content = self._remove_beams(result_content)
        
        return result_content
    
    def _is_eighth_note_start(self, lines, index):
        """Check if this line starts an eighth note block."""
        # Look ahead a few lines to see if this is an eighth note
        for i in range(index, min(index + 10, len(lines))):
            if '<type>eighth</type>' in lines[i]:
                return True
        return False
    
    def _extract_note_block(self, lines, start_index):
        """Extract a complete note block starting from start_index."""
        block = []
        i = start_index
        
        # Find the start of the note
        while i < len(lines) and '<note' not in lines[i]:
            block.append(lines[i])
            i += 1
        
        if i >= len(lines):
            return block, i
            
        # Add the note opening
        block.append(lines[i])
        i += 1
        
        # Continue until we find the closing note tag
        while i < len(lines) and '</note>' not in lines[i]:
            block.append(lines[i])
            i += 1
        
        # Add the closing note tag
        if i < len(lines):
            block.append(lines[i])
            i += 1
            
        return block, i
    
    def _is_eighth_note_block(self, block):
        """Check if this block represents an eighth note."""
        block_text = '\n'.join(block)
        return '<type>eighth</type>' in block_text and '<pitch>' in block_text
    
    def _is_eighth_rest_block(self, block):
        """Check if this block represents an eighth rest."""
        block_text = '\n'.join(block)
        return '<type>eighth</type>' in block_text and '<rest/>' in block_text
    
    def _convert_to_quarter_note(self, note_block):
        """Convert an eighth note block to a quarter note block."""
        converted_block = []
        
        for line in note_block:
            # Convert duration
            if '<duration>1</duration>' in line:
                converted_block.append(line.replace('<duration>1</duration>', '<duration>2</duration>'))
            # Convert type
            elif '<type>eighth</type>' in line:
                converted_block.append(line.replace('<type>eighth</type>', '<type>quarter</type>'))
            # Skip beam elements
            elif '<beam number=' in line:
                continue
            else:
                converted_block.append(line)
        
        return converted_block
    
    def _convert_to_quarter_rest(self, rest_block):
        """Convert an eighth rest block to a quarter rest block."""
        converted_block = []
        
        for line in rest_block:
            # Convert duration
            if '<duration>1</duration>' in line:
                converted_block.append(line.replace('<duration>1</duration>', '<duration>2</duration>'))
            # Convert type
            elif '<type>eighth</type>' in line:
                converted_block.append(line.replace('<type>eighth</type>', '<type>quarter</type>'))
            # Skip beam elements (shouldn't be in rests, but just in case)
            elif '<beam number=' in line:
                continue
            else:
                converted_block.append(line)
        
        return converted_block
    
    def _remove_beams(self, content):
        """Remove all beam elements from the content."""
        # Remove beam tags
        content = re.sub(r'\s*<beam number="[^"]*">[^<]*</beam>\s*\n?', '', content)
        return content
    
    def fix_rehearsal_marks(self, content, mode='measure_numbers'):
        """
        Fix rehearsal marks to be either sequential letters or measure numbers.
        
        Args:
            content: MusicXML content string
            mode: 'measure_numbers' or 'letters'
        """
        import re
        
        if mode == 'measure_numbers':
            # Find all measures and fix their rehearsal marks
            lines = content.split('\n')
            current_measure = None
            
            for i, line in enumerate(lines):
                # Track current measure
                measure_match = re.search(r'<measure number="(\d+)"', line)
                if measure_match:
                    current_measure = measure_match.group(1)
                
                # Fix rehearsal marks in current measure
                if current_measure and '<rehearsal' in line and i + 1 < len(lines):
                    # Look for the rehearsal content in the next few lines
                    for j in range(i, min(i + 5, len(lines))):
                        rehearsal_match = re.search(r'>([^<]+)</rehearsal>', lines[j])
                        if rehearsal_match:
                            current_mark = rehearsal_match.group(1)
                            if current_mark != current_measure:
                                self.rehearsal_marks_fixed += 1
                                print(f"  Fixed rehearsal mark: measure {current_measure} '{current_mark}' → '{current_measure}'")
                                lines[j] = lines[j].replace(f'>{current_mark}</rehearsal>', f'>{current_measure}</rehearsal>')
                            break
            
            content = '\n'.join(lines)
            
        elif mode == 'letters':
            # Convert to sequential letters A, B, C, D...
            rehearsal_pattern = r'(<rehearsal[^>]*>)([^<]+)(</rehearsal>)'
            letter_index = 0
            
            def replace_with_letters(match):
                nonlocal letter_index
                rehearsal_open = match.group(1)
                current_mark = match.group(2)
                rehearsal_close = match.group(3)
                
                new_letter = chr(ord('A') + letter_index)
                letter_index += 1
                
                if current_mark != new_letter:
                    self.rehearsal_marks_fixed += 1
                    print(f"  Fixed rehearsal mark: '{current_mark}' → '{new_letter}'")
                
                return rehearsal_open + new_letter + rehearsal_close
            
            content = re.sub(rehearsal_pattern, replace_with_letters, content)
        
        return content
    
    def center_title(self, content):
        """
        Center the main title in the MusicXML credit section.
        
        Finds the first credit-words element with large font size (title)
        and centers it horizontally and positions it properly vertically.
        """
        
        # First, find the page width to calculate center position
        page_width_match = re.search(r'<page-width>([\d.]+)</page-width>', content)
        if not page_width_match:
            print("  Warning: Could not find page width, using default center position")
            center_x = "616.935"  # Default center for standard page
        else:
            page_width = float(page_width_match.group(1))
            center_x = str(page_width / 2)
        
        # Position title at the bottom of the header area to avoid conflicts
        # Use a fixed position that's well below any typical header elements
        page_height_match = re.search(r'<page-height>([\d.]+)</page-height>', content)
        if page_height_match:
            page_height = float(page_height_match.group(1))
            # Position title at about 15% down from top (85% of page height)
            title_y = str(page_height * 0.85)
            print(f"  Positioning title at bottom of header area: Y={title_y} (85% of page height)")
        else:
            # Fallback to a low position in the header
            title_y = "1350"
            print(f"  Using fallback title position: Y={title_y}")
        
        # Target specifically the title element (the one WITHOUT font-size="14")
        # Step 1: Update X coordinate (horizontal centering) - only for non-part-name elements
        content = re.sub(
            r'(<credit-words(?![^>]*font-size="14")[^>]*default-x=")[^"]*(")',
            lambda m: m.group(1) + center_x + m.group(2),
            content
        )
        
        # Step 2: Update Y coordinate (vertical positioning) - only for non-part-name elements
        content = re.sub(
            r'(<credit-words(?![^>]*font-size="14")[^>]*default-y=")[^"]*(")',
            lambda m: m.group(1) + title_y + m.group(2),
            content
        )
        
        # Step 3: Update justify to center - only for non-part-name elements
        content = re.sub(
            r'(<credit-words(?![^>]*font-size="14")[^>]*justify=")left(")',
            lambda m: m.group(1) + "center" + m.group(2),
            content
        )
        
        print(f"  Centering title")
        print(f"  Position: x={center_x}, y={title_y}")
        
        return content
    
    def sync_part_names(self, content, new_part_name):
        """
        Synchronize all part name references throughout the MusicXML file.
        
        Updates part names in:
        1. Header metadata (miscellaneous-field partName)
        2. Visual credit display (credit-words)
        3. Part definition (part-name in score-part)
        
        Args:
            content: MusicXML content as string
            new_part_name: New name to apply to all part name locations
        """
        
        print(f"  Updating part name to: '{new_part_name}'")
        
        # 1. Update header metadata (miscellaneous-field)
        metadata_pattern = r'(<miscellaneous-field name="partName">)[^<]*(</miscellaneous-field>)'
        content = re.sub(metadata_pattern, r'\1' + new_part_name + r'\2', content)
        
        # 2. Update visual credit display (find credit-words with part name)
        # Look for credit-words that contain typical part names (contains "Part" or instrument names)
        credit_pattern = r'(<credit-words[^>]*>)([^<]*(?:Part|Trumpet|Trombone|Tuba|Horn|Flute|Clarinet|Saxophone|Violin|Viola|Cello|Bass|Piano|Guitar|Drum)[^<]*)(</credit-words>)'
        
        def replace_credit_part_name(match):
            opening_tag = match.group(1)
            old_name = match.group(2)
            closing_tag = match.group(3)
            
            # Only replace if it looks like a part name (not composer info)
            if any(word in old_name.lower() for word in ['part', 'trumpet', 'trombone', 'tuba', 'horn', 'flute', 'clarinet', 'sax', 'violin', 'viola', 'cello', 'bass', 'piano', 'guitar', 'drum']):
                print(f"    Credit display: '{old_name.strip()}' → '{new_part_name}'")
                return opening_tag + new_part_name + closing_tag
            return match.group(0)  # No change if not a part name
        
        content = re.sub(credit_pattern, replace_credit_part_name, content)
        
        # 3. Update part definition (part-name in score-part)
        part_def_pattern = r'(<part-name>)[^<]*(</part-name>)'
        
        def replace_part_definition(match):
            opening_tag = match.group(1) 
            closing_tag = match.group(2)
            print(f"    Part definition: updated to '{new_part_name}'")
            return opening_tag + new_part_name + closing_tag
        
        content = re.sub(part_def_pattern, replace_part_definition, content)
        
        return content
    
    def clean_credit_text(self, content):
        """
        Clean up credit text formatting for better MuseScore compatibility.
        
        1. Joins lines within individual credit-words elements
        2. Consolidates multiple credit-words elements in the same credit block  
        3. Replaces problematic characters that can cause truncation in MuseScore
        4. Normalizes whitespace
        
        MuseScore and many other notation programs can truncate credit text when they
        encounter certain special characters or XML entities. This function ensures
        maximum compatibility by converting problematic characters to safe alternatives.
        """
        
        print("Cleaning up credit text formatting...")
        
        # First, clean up individual credit-words elements (join internal newlines)
        credit_pattern = r'(<credit-words[^>]*>)(.*?)(</credit-words>)'
        
        def clean_credit_content(match):
            opening_tag = match.group(1)
            content_text = match.group(2)
            closing_tag = match.group(3)
            
            # Clean the content: join lines with spaces and normalize whitespace
            cleaned_text = re.sub(r'\s*\n\s*', ' ', content_text.strip())
            cleaned_text = re.sub(r'\s+', ' ', cleaned_text)
            
            return opening_tag + cleaned_text + closing_tag
        
        # Apply the cleanup using DOTALL flag to match across newlines
        content = re.sub(credit_pattern, clean_credit_content, content, flags=re.DOTALL)
        
        # Second, consolidate multiple credit-words elements within the same credit block
        # This is crucial for MuseScore compatibility
        credit_block_pattern = r'(<credit[^>]*>)(.*?)(</credit>)'
        
        def consolidate_credit_words(match):
            opening_credit = match.group(1)
            credit_content = match.group(2)
            closing_credit = match.group(3)
            
            # Find all credit-words elements in this credit block
            words_pattern = r'<credit-words([^>]*)>([^<]*)</credit-words>'
            credit_words_matches = list(re.finditer(words_pattern, credit_content))
            
            if len(credit_words_matches) <= 1:
                return match.group(0)  # No consolidation needed
            
            # Extract attributes from the first credit-words (positioning, formatting)
            first_attributes = credit_words_matches[0].group(1)
            
            # Collect all text content and decode HTML entities
            all_text = []
            for words_match in credit_words_matches:
                text = words_match.group(2).strip()
                if text:  # Only add non-empty text
                    # Decode HTML entities and replace problematic characters for MuseScore compatibility
                    text = text.replace('&amp;', 'and')  # Replace & with "and" for better compatibility
                    text = text.replace('&lt;', '<')
                    text = text.replace('&gt;', '>')
                    text = text.replace('&quot;', '"')
                    text = text.replace('&#39;', "'")
                    text = text.replace('&apos;', "'")
                    
                    # Handle additional problematic characters that may cause truncation
                    text = text.replace('©', '(c)')      # Copyright symbol
                    text = text.replace('®', '(r)')      # Registered trademark
                    text = text.replace('™', '(tm)')     # Trademark symbol
                    text = text.replace('°', 'deg')      # Degree symbol
                    text = text.replace('†', '+')        # Dagger symbol
                    text = text.replace('‡', '++')       # Double dagger
                    text = text.replace('§', 'section')  # Section symbol
                    text = text.replace('¶', 'para')     # Paragraph symbol
                    
                    # Handle common Unicode quotes and dashes that may cause issues
                    text = text.replace('"', '"')        # Left double quote
                    text = text.replace('"', '"')        # Right double quote  
                    text = text.replace(''', "'")        # Left single quote
                    text = text.replace(''', "'")        # Right single quote
                    text = text.replace('–', '-')        # En dash
                    text = text.replace('—', '--')       # Em dash
                    text = text.replace('…', '...')      # Ellipsis
                    
                    # Handle musical symbols that might be problematic in credits
                    text = text.replace('♭', 'b')        # Flat symbol
                    text = text.replace('♯', '#')        # Sharp symbol
                    text = text.replace('♮', 'natural')  # Natural symbol
                    
                    # Handle fraction symbols
                    text = text.replace('½', '1/2')
                    text = text.replace('¼', '1/4') 
                    text = text.replace('¾', '3/4')
                    text = text.replace('⅓', '1/3')
                    text = text.replace('⅔', '2/3')
                    all_text.append(text)
            
            if not all_text:
                return match.group(0)  # No text to consolidate
            
            # Join all text with spaces - let MuseScore handle word wrapping
            consolidated_text = ' - '.join(all_text)
            
            # Create new consolidated credit-words element
            new_credit_words = f'    <credit-words{first_attributes}>{consolidated_text}</credit-words>'
            
            # Remove the old credit-words elements and replace with consolidated one
            cleaned_content = re.sub(r'\s*<credit-words[^>]*>[^<]*</credit-words>\s*', '', credit_content)
            cleaned_content = cleaned_content.strip() + '\n' + new_credit_words + '\n    '
            
            print(f"  Consolidated {len(credit_words_matches)} credit-words into single element")
            
            return opening_credit + cleaned_content + closing_credit
        
        # Apply credit block consolidation using DOTALL flag
        content = re.sub(credit_block_pattern, consolidate_credit_words, content, flags=re.DOTALL)
        
        return content
    
    def remove_multimeasure_rests(self, content):
        """
        Convert multi-measure rests into individual measure rests for easier counting.
        
        Multi-measure rests (like a rest spanning 4 measures) can be confusing for
        beginners. This converts them into separate single-measure rests that are
        easier to count and follow along with.
        
        Handles both:
        1. <multiple-rest>N</multiple-rest> notation
        2. Individual measures with <rest measure="yes"/> in sequence
        """
        
        print("Removing multi-measure rests...")
        
        multimeasure_rests_removed = 0
        
        # First, handle explicit <multiple-rest> elements and remove them
        # These indicate how many measures the rest spans
        multiple_rest_pattern = r'<measure-style>\s*<multiple-rest>(\d+)</multiple-rest>\s*</measure-style>'
        
        def remove_multiple_rest_directive(match):
            nonlocal multimeasure_rests_removed
            count = int(match.group(1))
            multimeasure_rests_removed += 1
            print(f"  Removing {count}-measure rest directive")
            return ''  # Remove the multiple-rest directive entirely
        
        content = re.sub(multiple_rest_pattern, remove_multiple_rest_directive, content)
        
        # Second, convert all <rest measure="yes"/> to regular rests
        # This standardizes how rests appear for beginners
        measure_rest_pattern = r'<rest[^>]*measure="yes"[^>]*/>'
        
        def convert_measure_rest(match):
            print(f"  Converting measure rest to standard rest")
            return '<rest/>'
        
        content = re.sub(measure_rest_pattern, convert_measure_rest, content)
        
        # Also handle the self-closing version
        measure_rest_pattern2 = r'<rest[^>]*measure="yes"[^>]*></rest>'
        content = re.sub(measure_rest_pattern2, '<rest></rest>', content)
        
        self.multimeasure_rests_removed = multimeasure_rests_removed
        return content
    
    def simplify_file(self, input_path, output_path, rules='downbeat', fix_rehearsal='measure_numbers', center_title=False, sync_part_names=None, clean_credits=True, remove_multimeasure_rests=False):
        """
        Simplify a MusicXML file and save the result.
        
        Args:
            input_path: Path to input MusicXML file
            output_path: Path for output file
            rules: Which rule set to apply ('downbeat', etc.)
        """
        
        # Read input file
        try:
            with open(input_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            print(f"Error reading input file: {e}")
            return False
        
        # Apply rules
        if rules == 'downbeat':
            simplified_content = self.apply_downbeat_rules(content)
            self.rules_applied.append('downbeat_simplification')
        else:
            print(f"Unknown rule set: {rules}")
            return False
        
        # Fix rehearsal marks if requested
        if fix_rehearsal:
            print(f"\nFixing rehearsal marks (mode: {fix_rehearsal})...")
            simplified_content = self.fix_rehearsal_marks(simplified_content, fix_rehearsal)
        
        # Center title if requested
        if center_title:
            print(f"\nCentering title...")
            simplified_content = self.center_title(simplified_content)
        
        # Sync part names if requested
        if sync_part_names:
            print(f"\nSynchronizing part names...")
            simplified_content = self.sync_part_names(simplified_content, sync_part_names)
            if self.rehearsal_marks_fixed > 0:
                self.rules_applied.append(f'rehearsal_marks_{fix_rehearsal}')
        
        # Clean up credit text formatting if requested
        if clean_credits:
            print(f"\nCleaning credit text...")
            simplified_content = self.clean_credit_text(simplified_content)
        
        # Remove multi-measure rests if requested
        if remove_multimeasure_rests:
            print(f"\nRemoving multi-measure rests...")
            simplified_content = self.remove_multimeasure_rests(simplified_content)
        
        # Update title/metadata to indicate simplification
        # Only auto-update part name if we're not using custom part names
        if not sync_part_names:
            simplified_content = self._update_metadata(simplified_content)
        else:
            # Just update the software credit, not the part name
            simplified_content = self._update_software_credit(simplified_content)
        
        # Write output file
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(simplified_content)
        except Exception as e:
            print(f"Error writing output file: {e}")
            return False
        
        return True
    
    def _update_metadata(self, content):
        """Update the file metadata to indicate it's been simplified."""
        # Update part name
        content = re.sub(
            r'(<miscellaneous-field name="partName">.*?)(</miscellaneous-field>)',
            r'\1 - Simplified\2',
            content
        )
        
        # Update software credit
        content = self._update_software_credit(content)
        
        return content
    
    def _update_software_credit(self, content):
        """Update just the software credit to indicate processing by MusicXML Simplifier."""
        content = re.sub(
            r'(<software>.*?)(</software>)',
            r'\1 - Simplified by MusicXML Simplifier\2',
            content
        )
        
        return content
    
    def print_summary(self):
        """Print a summary of the simplification process."""
        print(f"\n=== Simplification Summary ===")
        print(f"Measures processed: {self.measures_processed}")
        print(f"Eighth notes converted: {self.eighth_notes_converted}")
        print(f"Rehearsal marks fixed: {self.rehearsal_marks_fixed}")
        print(f"Multi-measure rests removed: {self.multimeasure_rests_removed}")
        print(f"Rules applied: {', '.join(self.rules_applied)}")
        print("=== End Summary ===\n")


def main():
    """Main function for command-line usage."""
    parser = argparse.ArgumentParser(
        description='Simplify MusicXML files for beginner musicians',
        epilog='Example: python musicxml_simplifier.py input.musicxml output.musicxml'
    )
    
    parser.add_argument('input', help='Input MusicXML file path')
    parser.add_argument('output', help='Output MusicXML file path')
    parser.add_argument('--rules', default='downbeat', 
                       choices=['downbeat'],
                       help='Rule set to apply (default: downbeat)')
    parser.add_argument('--rehearsal', default='measure_numbers',
                       choices=['measure_numbers', 'letters', 'none'],
                       help='Fix rehearsal marks: measure_numbers, letters, or none (default: measure_numbers)')
    parser.add_argument('--center-title', action='store_true',
                       help='Center the main title horizontally on the page')
    parser.add_argument('--sync-part-names', type=str, metavar='NAME',
                       help='Update all part name references to the specified name (e.g., "Part 3 Trumpet Easy")')
    parser.add_argument('--no-clean-credits', action='store_true',
                       help='Skip cleaning up multi-line credit text (credit cleaning is enabled by default)')
    parser.add_argument('--remove-multimeasure-rests', action='store_true',
                       help='Convert multi-measure rests into individual measure rests for easier counting')
    parser.add_argument('--verbose', '-v', action='store_true',
                       help='Print detailed progress information')
    
    args = parser.parse_args()
    
    # Validate input file
    input_path = Path(args.input)
    if not input_path.exists():
        print(f"Error: Input file '{args.input}' not found")
        sys.exit(1)
    
    if not input_path.suffix.lower() in ['.musicxml', '.xml']:
        print(f"Warning: Input file doesn't have .musicxml or .xml extension")
    
    # Create simplifier and process file
    simplifier = MusicXMLSimplifier()
    
    print(f"Simplifying '{args.input}' → '{args.output}'")
    print(f"Using rule set: {args.rules}")
    if args.rehearsal != 'none':
        print(f"Rehearsal mark mode: {args.rehearsal}")
    if args.center_title:
        print(f"Title centering: enabled")
    if args.sync_part_names:
        print(f"Part name sync: '{args.sync_part_names}'")
    
    rehearsal_mode = None if args.rehearsal == 'none' else args.rehearsal
    clean_credits = not args.no_clean_credits  # Clean credits by default, disable with --no-clean-credits
    success = simplifier.simplify_file(args.input, args.output, args.rules, rehearsal_mode, args.center_title, args.sync_part_names, clean_credits, args.remove_multimeasure_rests)
    
    if success:
        print("✓ Simplification completed successfully!")
        simplifier.print_summary()
    else:
        print("✗ Simplification failed!")
        sys.exit(1)


if __name__ == '__main__':
    main()