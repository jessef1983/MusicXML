#!/usr/bin/env python3
"""
MusicXML Rhythm Simplifier

A tool for simplifying complex rhythms in MusicXML files to make them
more accessible for beginner musicians.

Author: GitHub Copilot
Date: 2025-10-23
"""

import re

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
        self.courtesy_accidentals_added = 0
        self.trumpet_fingerings_added = 0
        
        # Instrument correction definitions
        self.INSTRUMENT_CORRECTIONS = {
            'bb_trumpet': {
                'name': 'Trumpet',
                'part_name': 'Trumpet in Bb',  # Proper part name with transposition info
                'transpose_chromatic': -2,  # Written to concert: written C -> concert Bb (DOWN 2 semitones)
                'transpose_diatonic': -1,   # Written to concert: written C -> concert Bb (DOWN 1 diatonic step)
                'instrument_sound': 'brass.trumpet.bflat',
                'midi_program': 57  # Trumpet
            },
            'concert_pitch': {
                'name': 'Concert Pitch',
                'part_name': 'Concert Pitch',
                'transpose_chromatic': 0,   # No transposition
                'transpose_diatonic': 0,
                'instrument_sound': 'keyboard.piano',
                'midi_program': 1   # Piano (neutral)
            },
            'flute': {
                'name': 'Flute',
                'part_name': 'Flute',
                'transpose_chromatic': 0,   # No transposition (concert pitch)
                'transpose_diatonic': 0,
                'instrument_sound': 'wind.flutes.flute',
                'midi_program': 74   # Flute
            },
            'eb_alto_sax': {
                'name': 'Alto Saxophone',
                'part_name': 'Alto Saxophone in Eb',
                'transpose_chromatic': -9,  # Written to concert: written C -> concert Eb (DOWN 9 semitones = major 6th)
                'transpose_diatonic': -5,   # Written to concert: DOWN 5 diatonic steps
                'instrument_sound': 'reed.saxophone.alto',
                'midi_program': 66  # Alto Sax
            },
            'f_horn': {
                'name': 'Horn',
                'part_name': 'Horn in F',
                'transpose_chromatic': -7,  # Written to concert: written C -> concert F (DOWN 7 semitones = perfect 5th)
                'transpose_diatonic': -4,   # Written to concert: DOWN 4 diatonic steps
                'instrument_sound': 'brass.french-horn',
                'midi_program': 61  # French Horn
            },
            'bb_clarinet': {
                'name': 'Clarinet',
                'part_name': 'Clarinet in Bb',
                'transpose_chromatic': -2,  # Written to concert: written C -> concert Bb (DOWN 2 semitones)
                'transpose_diatonic': -1,   # Written to concert: DOWN 1 diatonic step
                'instrument_sound': 'wind.reed.clarinet.bflat',
                'midi_program': 72  # Clarinet
            }
        }
        
        # Alto Saxophone Fingering Chart Database
        # Key: (step, alter, octave) - Value: {'fingering': str, 'holes': [bool, ...]}
        # Holes represent: [LH-Thumb, LH-1, LH-2, LH-3, RH-1, RH-2, RH-3, RH-4, Octave-Key]
        # True = closed/pressed, False = open
        self.ALTO_SAX_FINGERINGS = {
            # Lower register - Bb3 to C5 (no octave key)
            ('B', -1, 3): {'fingering': '123 123C', 'holes': [True, True, True, True, True, True, True, True, False]},  # Bb3 (low Bb with C key)
            ('B', 0, 3): {'fingering': '123 123', 'holes': [True, True, True, True, True, True, True, False, False]},   # B3 (low B)
            ('C', 0, 4): {'fingering': '123 12', 'holes': [True, True, True, True, True, True, False, False, False]},   # C4 (low C)
            ('C', 1, 4): {'fingering': '123 1', 'holes': [True, True, True, True, True, False, False, False, False]},   # C#4 (low C#)
            ('D', -1, 4): {'fingering': '123 1', 'holes': [True, True, True, True, True, False, False, False, False]},  # Db4 (same as C#4)
            ('D', 0, 4): {'fingering': '123', 'holes': [True, True, True, True, False, False, False, False, False]},    # D4 (low D)
            ('D', 1, 4): {'fingering': '12', 'holes': [True, True, True, False, False, False, False, False, False]},    # D#4 (Eb)
            ('E', -1, 4): {'fingering': '12', 'holes': [True, True, True, False, False, False, False, False, False]},   # Eb4 (same as D#4)
            ('E', 0, 4): {'fingering': '1', 'holes': [True, True, False, False, False, False, False, False, False]},    # E4
            ('F', 0, 4): {'fingering': '1 1', 'holes': [True, True, False, False, True, False, False, False, False]},   # F4 (cross fingering)
            ('F', 1, 4): {'fingering': '123 12 LowC', 'holes': [True, True, True, True, True, True, False, False, False]},   # F#4 (fork fingering with right pinky low side key)
            ('G', -1, 4): {'fingering': '123 12 LowC', 'holes': [True, True, True, True, True, True, False, False, False]},  # Gb4 (same as F#4)
            ('G', 0, 4): {'fingering': 'T', 'holes': [True, False, False, False, False, False, False, False, False]},    # G4 (thumb only)
            ('G', 1, 4): {'fingering': '23 123', 'holes': [True, False, True, True, True, True, True, False, False]},   # G#4 (Ab)
            ('A', -1, 4): {'fingering': '23 123', 'holes': [True, False, True, True, True, True, True, False, False]}, # Ab4 (same as G#4)
            ('A', 0, 4): {'fingering': '2 123', 'holes': [True, False, True, False, True, True, True, False, False]},  # A4
            ('A', 1, 4): {'fingering': '2 12', 'holes': [True, False, True, False, True, True, False, False, False]},  # A#4 (Bb)
            ('B', -1, 4): {'fingering': '2 12', 'holes': [True, False, True, False, True, True, False, False, False]}, # Bb4 (same as A#4)
            ('B', 0, 4): {'fingering': '2', 'holes': [True, False, True, False, False, False, False, False, False]},   # B4
            ('C', 0, 5): {'fingering': '2 1', 'holes': [True, False, True, False, True, False, False, False, False]},  # C5 (middle space)
            
            # Upper register - C#5 and above (requires octave key - should be transposed down)
            ('C', 1, 5): {'fingering': 'Oct', 'holes': [True, False, False, False, False, False, False, False, True]},  # C#5 (octave key only)
            ('D', -1, 5): {'fingering': 'Oct', 'holes': [True, False, False, False, False, False, False, False, True]}, # Db5 (same as C#5)
            ('D', 0, 5): {'fingering': '123 123 Oct', 'holes': [True, True, True, True, True, True, True, False, True]}, # D5 (all fingers + octave)
            ('D', 1, 5): {'fingering': '12 1 Oct', 'holes': [True, True, True, False, True, False, False, False, True]}, # D#5
            ('E', -1, 5): {'fingering': '12 1 Oct', 'holes': [True, True, True, False, True, False, False, False, True]}, # Eb5 (same as D#5)
            ('E', 0, 5): {'fingering': '12 12 Oct', 'holes': [True, True, True, False, True, True, False, False, True]}, # E5
            ('F', 0, 5): {'fingering': '1 12 Oct', 'holes': [True, True, False, False, True, True, False, False, True]}, # F5
            ('F', 1, 5): {'fingering': '1 2 Oct', 'holes': [True, True, False, True, False, False, False, False, True]}, # F#5
            ('G', -1, 5): {'fingering': '1 2 Oct', 'holes': [True, True, False, True, False, False, False, False, True]}, # Gb5 (same as F#5)
            ('G', 0, 5): {'fingering': 'Oct', 'holes': [True, False, False, False, False, False, False, False, True]}, # G5 (octave key only)
            ('A', 0, 5): {'fingering': '2 123 Oct', 'holes': [True, False, True, False, True, True, True, False, True]}, # A5 
            ('B', 0, 5): {'fingering': '2 Oct', 'holes': [True, False, True, False, False, False, False, False, True]}, # B5
        }
        
        # Bb Trumpet Fingering Chart Database
        # Key: (step, alter, octave) - Value: {'fingering': str, 'valves': [bool, bool, bool]}
        # Valves represent: [Valve-1, Valve-2, Valve-3] - True = pressed, False = open
        # Bb trumpet written pitch (sounds a whole step lower in concert pitch)
        self.BB_TRUMPET_FINGERINGS = {
            # Low register - written F#3 (concert E3) to written C5 (concert Bb4)
            ('F', 1, 3): {'fingering': '2', 'valves': [False, True, False]},    # F#3 (written, sounds E3)
            ('G', 0, 3): {'fingering': '0', 'valves': [False, False, False]},   # G3 (written, sounds F3) - open
            ('G', 1, 3): {'fingering': '23', 'valves': [False, True, True]},    # G#3 (written, sounds F#3)
            ('A', -1, 3): {'fingering': '23', 'valves': [False, True, True]},   # Ab3 (same as G#3)
            ('A', 0, 3): {'fingering': '12', 'valves': [True, True, False]},    # A3 (written, sounds G3)
            ('A', 1, 3): {'fingering': '1', 'valves': [True, False, False]},    # A#3 (written, sounds G#3)
            ('B', -1, 3): {'fingering': '1', 'valves': [True, False, False]},   # Bb3 (same as A#3)
            ('B', 0, 3): {'fingering': '2', 'valves': [False, True, False]},    # B3 (written, sounds A3)
            
            # Middle register - written C4 to written C5 (most common range)
            ('C', 0, 4): {'fingering': '0', 'valves': [False, False, False]},   # C4 (written, sounds Bb3) - open
            ('C', 1, 4): {'fingering': '23', 'valves': [False, True, True]},    # C#4 (written, sounds B3)
            ('D', -1, 4): {'fingering': '23', 'valves': [False, True, True]},   # Db4 (same as C#4)
            ('D', 0, 4): {'fingering': '13', 'valves': [True, False, True]},    # D4 (written, sounds C4)
            ('D', 1, 4): {'fingering': '2', 'valves': [False, True, False]},    # D#4 (written, sounds C#4)
            ('E', -1, 4): {'fingering': '2', 'valves': [False, True, False]},   # Eb4 (same as D#4)
            ('E', 0, 4): {'fingering': '12', 'valves': [True, True, False]},    # E4 (written, sounds D4)
            ('F', 0, 4): {'fingering': '1', 'valves': [True, False, False]},    # F4 (written, sounds Eb4)
            ('F', 1, 4): {'fingering': '2', 'valves': [False, True, False]},    # F#4 (written, sounds E4)
            ('G', -1, 4): {'fingering': '2', 'valves': [False, True, False]},   # Gb4 (same as F#4)
            ('G', 0, 4): {'fingering': '0', 'valves': [False, False, False]},   # G4 (written, sounds F4) - open
            ('G', 1, 4): {'fingering': '23', 'valves': [False, True, True]},    # G#4 (written, sounds F#4)
            ('A', -1, 4): {'fingering': '23', 'valves': [False, True, True]},   # Ab4 (same as G#4)
            ('A', 0, 4): {'fingering': '12', 'valves': [True, True, False]},    # A4 (written, sounds G4)
            ('A', 1, 4): {'fingering': '1', 'valves': [True, False, False]},    # A#4 (written, sounds G#4)
            ('B', -1, 4): {'fingering': '1', 'valves': [True, False, False]},   # Bb4 (same as A#4)
            ('B', 0, 4): {'fingering': '2', 'valves': [False, True, False]},    # B4 (written, sounds A4)
            ('C', 0, 5): {'fingering': '0', 'valves': [False, False, False]},   # C5 (written, sounds Bb4) - open
            
            # Upper register - written C#5 and above (for advanced players)
            ('C', 1, 5): {'fingering': '23', 'valves': [False, True, True]},    # C#5 (written, sounds B4)
            ('D', -1, 5): {'fingering': '23', 'valves': [False, True, True]},   # Db5 (same as C#5)
            ('D', 0, 5): {'fingering': '13', 'valves': [True, False, True]},    # D5 (written, sounds C5)
            ('D', 1, 5): {'fingering': '2', 'valves': [False, True, False]},    # D#5 (written, sounds C#5)
            ('E', -1, 5): {'fingering': '2', 'valves': [False, True, False]},   # Eb5 (same as D#5)
            ('E', 0, 5): {'fingering': '12', 'valves': [True, True, False]},    # E5 (written, sounds D5)
            ('F', 0, 5): {'fingering': '1', 'valves': [True, False, False]},    # F5 (written, sounds Eb5)
            ('F', 1, 5): {'fingering': '2', 'valves': [False, True, False]},    # F#5 (written, sounds E5)
            ('G', -1, 5): {'fingering': '2', 'valves': [False, True, False]},   # Gb5 (same as F#5)
            ('G', 0, 5): {'fingering': '0', 'valves': [False, False, False]},   # G5 (written, sounds F5) - open
        }
        
        # F Horn Fingering Chart Database
        # Key: (step, alter, octave) - Value: {'fingering': str, 'valves': [bool, bool, bool]}
        # Valves represent: [Valve-1, Valve-2, Valve-3] - True = pressed, False = open
        # F horn written pitch (sounds a perfect fifth lower in concert pitch)
        # Note: F horn fingerings are more complex due to hand stopping and alternate fingerings
        self.F_HORN_FINGERINGS = {
            # Low register - written B3 to written C5 (most common range)
            ('B', 0, 3): {'fingering': '123', 'valves': [True, True, True]},    # B3 (written, sounds E3)
            ('C', 0, 4): {'fingering': '12', 'valves': [True, True, False]},    # C4 (written, sounds F3)
            ('C', 1, 4): {'fingering': '2', 'valves': [False, True, False]},    # C#4 (written, sounds F#3)
            ('D', -1, 4): {'fingering': '2', 'valves': [False, True, False]},   # Db4 (same as C#4)
            ('D', 0, 4): {'fingering': '1', 'valves': [True, False, False]},    # D4 (written, sounds G3)
            ('D', 1, 4): {'fingering': '23', 'valves': [False, True, True]},    # D#4 (written, sounds G#3)
            ('E', -1, 4): {'fingering': '23', 'valves': [False, True, True]},   # Eb4 (same as D#4)
            ('E', 0, 4): {'fingering': '12', 'valves': [True, True, False]},    # E4 (written, sounds A3)
            ('F', 0, 4): {'fingering': '1', 'valves': [True, False, False]},    # F4 (written, sounds Bb3)
            ('F', 1, 4): {'fingering': '2', 'valves': [False, True, False]},    # F#4 (written, sounds B3)
            ('G', -1, 4): {'fingering': '2', 'valves': [False, True, False]},   # Gb4 (same as F#4)
            ('G', 0, 4): {'fingering': '0', 'valves': [False, False, False]},   # G4 (written, sounds C4) - open
            ('G', 1, 4): {'fingering': '23', 'valves': [False, True, True]},    # G#4 (written, sounds C#4)
            ('A', -1, 4): {'fingering': '23', 'valves': [False, True, True]},   # Ab4 (same as G#4)
            ('A', 0, 4): {'fingering': '12', 'valves': [True, True, False]},    # A4 (written, sounds D4)
            ('A', 1, 4): {'fingering': '1', 'valves': [True, False, False]},    # A#4 (written, sounds D#4)
            ('B', -1, 4): {'fingering': '1', 'valves': [True, False, False]},   # Bb4 (same as A#4)
            ('B', 0, 4): {'fingering': '2', 'valves': [False, True, False]},    # B4 (written, sounds E4)
            
            # Middle register - written C5 to written C6 (common upper range)
            ('C', 0, 5): {'fingering': '0', 'valves': [False, False, False]},   # C5 (written, sounds F4) - open
            ('C', 1, 5): {'fingering': '23', 'valves': [False, True, True]},    # C#5 (written, sounds F#4)
            ('D', -1, 5): {'fingering': '23', 'valves': [False, True, True]},   # Db5 (same as C#5)
            ('D', 0, 5): {'fingering': '12', 'valves': [True, True, False]},    # D5 (written, sounds G4)
            ('D', 1, 5): {'fingering': '1', 'valves': [True, False, False]},    # D#5 (written, sounds G#4)
            ('E', -1, 5): {'fingering': '1', 'valves': [True, False, False]},   # Eb5 (same as D#5)
            ('E', 0, 5): {'fingering': '2', 'valves': [False, True, False]},    # E5 (written, sounds A4)
            ('F', 0, 5): {'fingering': '0', 'valves': [False, False, False]},   # F5 (written, sounds Bb4) - open
            ('F', 1, 5): {'fingering': '23', 'valves': [False, True, True]},    # F#5 (written, sounds B4)
            ('G', -1, 5): {'fingering': '23', 'valves': [False, True, True]},   # Gb5 (same as F#5)
            ('G', 0, 5): {'fingering': '12', 'valves': [True, True, False]},    # G5 (written, sounds C5)
            ('G', 1, 5): {'fingering': '1', 'valves': [True, False, False]},    # G#5 (written, sounds C#5)
            ('A', -1, 5): {'fingering': '1', 'valves': [True, False, False]},   # Ab5 (same as G#5)
            ('A', 0, 5): {'fingering': '2', 'valves': [False, True, False]},    # A5 (written, sounds D5)
            ('A', 1, 5): {'fingering': '0', 'valves': [False, False, False]},   # A#5 (written, sounds D#5) - open
            ('B', -1, 5): {'fingering': '0', 'valves': [False, False, False]},  # Bb5 (same as A#5) - open
            ('B', 0, 5): {'fingering': '23', 'valves': [False, True, True]},    # B5 (written, sounds E5)
            ('C', 0, 6): {'fingering': '12', 'valves': [True, True, False]},    # C6 (written, sounds F5)
        }
        
    def apply_downbeat_rules(self, content):
        """
        Apply downbeat simplification rules to MusicXML content.
        
        Rules:
        1. Convert dotted quarter + eighth note patterns to half notes
        2. Convert eighth note pairs to quarter notes
        3. Keep first note's pitch and articulation
        4. Handle rests appropriately
        5. Remove beam elements and dots as needed
        6. Maintain measure timing
        """
        
        lines = content.split('\n')
        result_lines = []
        i = 0
        
        while i < len(lines):
            line = lines[i]
            
            # Track measures for progress
            if '<measure number=' in line:
                self.measures_processed += 1
                
            # Look for dotted quarter + eighth note patterns to convert
            if self._is_dotted_quarter_start(lines, i):
                # Find the complete dotted quarter note block
                note_block, next_index = self._extract_note_block(lines, i)
                
                # Check if the next note is an eighth note
                if next_index < len(lines):
                    next_block, final_index = self._extract_note_block(lines, next_index)
                    
                    # If we have dotted quarter + eighth, convert to half note
                    if (self._is_dotted_quarter_block(note_block) and 
                        self._is_eighth_note_block(next_block)):
                        
                        # Convert dotted quarter to half note, swallow the eighth
                        simplified_block = self._convert_to_half_note(note_block)
                        result_lines.extend(simplified_block)
                        
                        # Skip the eighth note (it gets absorbed into the half)
                        i = final_index
                        self.eighth_notes_converted += 2  # Count as converting the pattern
                        continue
                
                # If not followed by eighth, add dotted quarter as-is
                result_lines.extend(note_block)
                i = next_index
                
            # Look for eighth note patterns to convert
            elif self._is_eighth_note_start(lines, i):
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
    
    def _is_dotted_quarter_start(self, lines, index):
        """Check if this line starts a dotted quarter note block."""
        # Look ahead a few lines to see if this is a dotted quarter note
        for i in range(index, min(index + 15, len(lines))):
            if '<type>quarter</type>' in lines[i]:
                # Check for dot in the next few lines (matches both <dot/> and <dot .../>)
                for j in range(i, min(i + 5, len(lines))):
                    if '<dot' in lines[j] and '/>' in lines[j]:
                        return True
        return False
    
    def _is_dotted_quarter_block(self, block):
        """Check if this block represents a dotted quarter note."""
        block_text = '\n'.join(block)
        return ('<type>quarter</type>' in block_text and 
                '<dot' in block_text and '/>' in block_text and 
                '<pitch>' in block_text)
    
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
            # Remove slur elements (since we're removing the paired eighth note that the slur connected to)
            elif '<slur' in line and ('type="start"' in line or 'type="stop"' in line):
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
    
    def _convert_to_half_note(self, dotted_quarter_block):
        """Convert a dotted quarter note block to a half note block."""
        converted_block = []
        duration_changed = False
        
        for line in dotted_quarter_block:
            # Convert duration from 3 (dotted quarter) to 4 (half note)
            if '<duration>3</duration>' in line:
                converted_block.append(line.replace('<duration>3</duration>', '<duration>4</duration>'))
                duration_changed = True
            # Convert type from quarter to half ONLY if we changed duration=3 to 4
            elif '<type>quarter</type>' in line and duration_changed:
                converted_block.append(line.replace('<type>quarter</type>', '<type>half</type>'))
            # Remove dot element (handles both <dot/> and <dot .../>)
            elif '<dot' in line and '/>' in line:
                continue
            # Skip beam elements
            elif '<beam number=' in line:
                continue
            # Remove slur elements that would span multiple notes (no longer needed for single half note)
            elif '<slur' in line and ('type="start"' in line or 'type="stop"' in line):
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
                                print(f"  Fixed rehearsal mark: measure {current_measure} '{current_mark}' -> '{current_measure}'")
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
                    print(f"  Fixed rehearsal mark: '{current_mark}' -> '{new_letter}'")
                
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
    
    def correct_instrument_metadata(self, content, instrument_key, update_part_names=False):
        """
        Correct instrument metadata to match the specified source instrument.
        Fixes transposition, instrument sound, and MIDI program settings.
        
        Args:
            content: MusicXML content as string
            instrument_key: Key from INSTRUMENT_CORRECTIONS dict
            update_part_names: Whether to also update part names to match instrument
        """
        if instrument_key not in self.INSTRUMENT_CORRECTIONS:
            print(f"  Warning: Unknown instrument '{instrument_key}', skipping correction")
            return content
            
        correction = self.INSTRUMENT_CORRECTIONS[instrument_key]
        print(f"  Correcting instrument metadata for: {correction['name']}")
        
        # Update transposition settings - only if incorrect or missing
        existing_transpose = re.search(r'<transpose>.*?<chromatic>([^<]+)</chromatic>.*?</transpose>', content, re.DOTALL)
        
        if correction['transpose_chromatic'] != 0:
            # Check if existing transposition is correct
            if existing_transpose:
                existing_chromatic = int(existing_transpose.group(1))
                if existing_chromatic == correction['transpose_chromatic']:
                    print(f"    Transposition already correct: {correction['transpose_chromatic']} semitones")
                else:
                    # Replace existing transpose block
                    transpose_block = f"""        <transpose>
          <diatonic>{correction['transpose_diatonic']}</diatonic>
          <chromatic>{correction['transpose_chromatic']}</chromatic>
        </transpose>"""
                    transpose_pattern = r'\s*<transpose>.*?</transpose>'
                    content = re.sub(transpose_pattern, '\n' + transpose_block, content, flags=re.DOTALL)
                    print(f"    Updated transposition: {existing_chromatic} -> {correction['transpose_chromatic']} semitones")
            else:
                # Add transpose block after clef
                transpose_block = f"""        <transpose>
          <diatonic>{correction['transpose_diatonic']}</diatonic>
          <chromatic>{correction['transpose_chromatic']}</chromatic>
        </transpose>"""
                clef_pattern = r'(\s*</clef>\s*)'
                replacement = r'\1' + transpose_block + '\n'
                content = re.sub(clef_pattern, replacement, content)
                print(f"    Added transposition: {correction['transpose_chromatic']} semitones")
        else:
            # Remove transposition for concert pitch
            if existing_transpose:
                transpose_pattern = r'\s*<transpose>.*?</transpose>\s*\n?'
                content = re.sub(transpose_pattern, '', content, flags=re.DOTALL)
                print("    Removed transposition (now concert pitch)")
        
        # Update instrument name
        name_pattern = r'(<instrument-name>)[^<]*(</instrument-name>)'
        if re.search(name_pattern, content):
            replacement = f'\\g<1>{correction["name"]}\\g<2>'
            content = re.sub(name_pattern, replacement, content)
            print(f"    Updated instrument name: {correction['name']}")
        
        # Update instrument sound
        sound_pattern = r'(<instrument-sound>)[^<]*(</instrument-sound>)'
        if re.search(sound_pattern, content):
            replacement = f'\\g<1>{correction["instrument_sound"]}\\g<2>'
            content = re.sub(sound_pattern, replacement, content)
            print(f"    Updated instrument sound: {correction['instrument_sound']}")
        
        # Update MIDI program
        program_pattern = r'(<midi-program>)[^<]*(</midi-program>)'
        if re.search(program_pattern, content):
            replacement = f'\\g<1>{correction["midi_program"]}\\g<2>'
            content = re.sub(program_pattern, replacement, content)
            print(f"    Updated MIDI program: {correction['midi_program']}")
        
        # Convert written key signature to concert key signature
        if correction['transpose_chromatic'] != 0:
            content = self.convert_to_concert_key_signature(content, correction['transpose_chromatic'])
        
        # Update part names if requested
        if update_part_names:
            print(f"    Updating part names to match corrected instrument...")
            part_name_to_use = correction.get('part_name', correction['name'])
            content = self.sync_part_names(content, part_name_to_use)
        
        return content
    
    def convert_to_concert_key_signature(self, content, transpose_chromatic):
        """
        Preserve written key signature for musicians while ensuring proper transpose element.
        
        The <key><fifths> should show the WRITTEN key (what musician reads on staff).
        The <transpose> element tells software how to convert to concert pitch.
        
        Args:
            content: MusicXML content as string
            transpose_chromatic: Chromatic transposition in semitones (negative = down)
            
        Returns:
            str: Content with preserved written key signature
        """
        # Find existing key signature
        key_match = re.search(r'<key>\s*<fifths>([^<]+)</fifths>\s*</key>', content)
        if not key_match:
            print("    No key signature found")
            return content
            
        written_fifths = int(key_match.group(1))
        written_key = self._fifths_to_key_name(written_fifths)
        
        # Calculate what the concert key would be for reference
        semitone_to_fifths = {
            -2: -2,   # Bb instrument (Trumpet, Clarinet)
            -7: -9,   # F instrument (French Horn)  
            9: 3,     # Eb instrument (Alto Sax)
            0: 0,     # Concert pitch
        }
        
        if transpose_chromatic in semitone_to_fifths:
            fifths_adjustment = semitone_to_fifths[transpose_chromatic]
            concert_fifths = written_fifths + fifths_adjustment
            
            # Clamp to valid range (-7 to +7 fifths)
            if concert_fifths < -7:
                concert_fifths += 12
            elif concert_fifths > 7:
                concert_fifths -= 12
                
            concert_key = self._fifths_to_key_name(concert_fifths)
            print(f"    Key signature: {written_key} (written) -> {concert_key} (concert)")
        else:
            print(f"    Key signature: {written_key} (written)")
        
        # Keep the written key signature as-is - do NOT change it
        # The <transpose> element handles the concert pitch conversion
        
        return content
    
    def _fifths_to_key_name(self, fifths):
        """Convert fifths value to key name."""
        key_names = {
            -7: "Cb major", -6: "Gb major", -5: "Db major", -4: "Ab major",
            -3: "Eb major", -2: "Bb major", -1: "F major", 0: "C major",
            1: "G major", 2: "D major", 3: "A major", 4: "E major",
            5: "B major", 6: "F# major", 7: "C# major"
        }
        return key_names.get(fifths, f"{fifths} fifths")
    
    def detect_part_name(self, content):
        """
        Detect the most authoritative part name from the MusicXML file.
        Priority: 1) score-part part-name, 2) metadata partName, 3) credit-words
        
        Args:
            content: MusicXML content as string
            
        Returns:
            str: The detected part name, or None if not found
        """
        
        # Priority 1: Check score-part part-name (most authoritative)
        part_name_match = re.search(r'<part-name>([^<]+)</part-name>', content)
        if part_name_match:
            part_name = part_name_match.group(1).strip()
            if part_name:
                print(f"  Detected part name from score-part: '{part_name}'")
                return part_name
        
        # Priority 2: Check metadata partName
        metadata_match = re.search(r'<miscellaneous-field name="partName">([^<]+)</miscellaneous-field>', content)
        if metadata_match:
            part_name = metadata_match.group(1).strip()
            if part_name:
                print(f"  Detected part name from metadata: '{part_name}'")
                return part_name
        
        # Priority 3: Check credit-words for instrument names
        credit_pattern = r'<credit-words[^>]*>([^<]*(?:Part|Trumpet|Trombone|Tuba|Horn|Flute|Clarinet|Saxophone|Violin|Viola|Cello|Bass|Piano|Guitar|Drum)[^<]*)</credit-words>'
        credit_matches = re.findall(credit_pattern, content, re.IGNORECASE)
        for credit_text in credit_matches:
            credit_text = credit_text.strip()
            if credit_text and len(credit_text) < 50:  # Reasonable length for part name
                print(f"  Detected part name from credit: '{credit_text}'")
                return credit_text
        
        print("  No part name detected")
        return None

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
        
        # 2. First, remove duplicate credit elements with identical part names
        # Find all credit blocks that contain part names
        credit_block_pattern = r'<credit[^>]*>.*?<credit-words[^>]*>([^<]*(?:Part|Trumpet|Trombone|Tuba|Horn|Flute|Clarinet|Saxophone|Violin|Viola|Cello|Bass|Piano|Guitar|Drum)[^<]*)</credit-words>.*?</credit>'
        
        credit_blocks = re.findall(credit_block_pattern, content, re.DOTALL)
        seen_part_names = set()
        
        def remove_duplicate_credits(match):
            credit_text = match.group(1).strip()
            full_match = match.group(0)
            
            # If this is a part name we've seen before, remove this credit block
            if any(word in credit_text.lower() for word in ['part', 'trumpet', 'trombone', 'tuba', 'horn', 'flute', 'clarinet', 'sax', 'violin', 'viola', 'cello', 'bass', 'piano', 'guitar', 'drum']):
                if credit_text in seen_part_names:
                    print(f"    Removing duplicate credit: '{credit_text}'")
                    return ''  # Remove the duplicate
                else:
                    seen_part_names.add(credit_text)
            
            return full_match  # Keep the first occurrence
        
        content = re.sub(credit_block_pattern, remove_duplicate_credits, content, flags=re.DOTALL)
        
        # 3. Now update the remaining credit displays
        credit_pattern = r'(<credit-words[^>]*>)([^<]*(?:Part|Trumpet|Trombone|Tuba|Horn|Flute|Clarinet|Saxophone|Violin|Viola|Cello|Bass|Piano|Guitar|Drum)[^<]*)(</credit-words>)'
        
        def replace_credit_part_name(match):
            opening_tag = match.group(1)
            old_name = match.group(2).strip()
            closing_tag = match.group(3)
            
            # Only replace if it looks like a part name
            if any(word in old_name.lower() for word in ['part', 'trumpet', 'trombone', 'tuba', 'horn', 'flute', 'clarinet', 'sax', 'violin', 'viola', 'cello', 'bass', 'piano', 'guitar', 'drum']):
                print(f"    Credit display: '{old_name}' -> '{new_part_name}'")
                return opening_tag + new_part_name + closing_tag
            return match.group(0)  # No change if not a part name
        
        content = re.sub(credit_pattern, replace_credit_part_name, content)
        
        # 3. Update part definition (part-name in score-part)
        part_def_pattern = r'(<part-name[^>]*>)[^<]*(</part-name>)'
        
        def replace_part_definition(match):
            opening_tag = match.group(1) 
            closing_tag = match.group(2)
            
            # Remove print-object="no" to make part name visible, or set it to "yes"
            if 'print-object="no"' in opening_tag:
                opening_tag = opening_tag.replace('print-object="no"', 'print-object="yes"')
                print(f"    Part definition: updated to '{new_part_name}' and made visible")
            else:
                print(f"    Part definition: updated to '{new_part_name}'")
            
            return opening_tag + new_part_name + closing_tag
        
        content = re.sub(part_def_pattern, replace_part_definition, content)
        
        return content
    
    def clean_credit_text(self, content):
        """
        Clean up credit text formatting for better MuseScore compatibility.
        
        1. Joins lines within individual credit-words elements
        2. Consolidates multiple credit-words elements in the same credit block  
        3. Removes duplicate credit blocks with identical text content
        4. Replaces problematic characters that can cause truncation in MuseScore
        5. Normalizes whitespace
        
        MuseScore and many other notation programs can truncate credit text when they
        encounter certain special characters or XML entities. This function ensures
        maximum compatibility by converting problematic characters to safe alternatives.
        """
        
        print("Cleaning up credit text formatting...")
        
        # First, remove duplicate credit blocks with identical text content
        seen_credit_texts = set()
        def remove_duplicate_credit_blocks(match):
            credit_content = match.group(2)
            # Extract just the text content from credit-words
            text_match = re.search(r'<credit-words[^>]*>([^<]*)</credit-words>', credit_content)
            if text_match:
                credit_text = text_match.group(1).strip()
                if credit_text in seen_credit_texts:
                    print(f"  Removing duplicate credit block: '{credit_text}'")
                    return ''  # Remove duplicate
                seen_credit_texts.add(credit_text)
            return match.group(0)  # Keep the first occurrence
        
        # Apply duplicate removal to entire credit blocks
        credit_block_pattern = r'(<credit[^>]*>)(.*?)(</credit>)'
        content = re.sub(credit_block_pattern, remove_duplicate_credit_blocks, content, flags=re.DOTALL)
        
        # Second, clean up individual credit-words elements (join internal newlines)
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
    
    def add_courtesy_accidentals(self, content):
        """
        Add courtesy accidentals to help C Major students.
        
        Pedagogical courtesy rules:
        1. First occurrence of any sharp or flat (because students learn C major)
        2. First occurrence after any written accidental (to remind students)
        
        This helps students learning C Major who need reminders about accidentals.
        
        Args:
            content: MusicXML content string
            
        Returns:
            Modified content with courtesy accidentals added
        """
        accidentals_added = 0
        
        # Track note states for each note name (regardless of octave)
        note_history = {}
        
        print("  Analyzing accidental patterns for C Major students...")
        
        # Extract measures for processing
        measure_pattern = r'<measure[^>]*number="(\d+)"[^>]*>(.*?)</measure>'
        
        # First pass: collect note history and written accidentals
        for match in re.finditer(measure_pattern, content, re.DOTALL):
            measure_num = int(match.group(1))
            measure_content = match.group(2)
            
            # Find all notes with pitch in this measure
            note_pattern = r'<note[^>]*>(.*?)</note>'
            for note_match in re.finditer(note_pattern, measure_content, re.DOTALL):
                note_content = note_match.group(1)
                
                # Check if this note has pitch
                pitch_match = re.search(r'<pitch>(.*?)</pitch>', note_content, re.DOTALL)
                if not pitch_match:
                    continue  # Skip rests
                
                pitch_content = pitch_match.group(1)
                
                # Extract step and alter
                step_match = re.search(r'<step>([A-G])</step>', pitch_content)
                alter_match = re.search(r'<alter>([-]?\d+)</alter>', pitch_content)
                accidental_match = re.search(r'<accidental[^>]*>([^<]+)</accidental>', note_content)
                
                if not step_match:
                    continue
                
                note_name = step_match.group(1)
                alter_value = int(alter_match.group(1)) if alter_match else 0
                
                # Initialize tracking for this note
                if note_name not in note_history:
                    note_history[note_name] = {
                        'first_sharp': None,
                        'first_flat': None,
                        'first_natural': None,
                        'last_written_accidental': None,
                        'needs_courtesy': set()
                    }
                
                history = note_history[note_name]
                
                # Track first encounters with sharp/flat/natural
                if alter_value == 1 and history['first_sharp'] is None:
                    history['first_sharp'] = measure_num
                    history['needs_courtesy'].add(measure_num)
                    print(f"    First {note_name}# at measure {measure_num} - needs courtesy")
                elif alter_value == -1 and history['first_flat'] is None:
                    history['first_flat'] = measure_num
                    history['needs_courtesy'].add(measure_num)
                    print(f"    First {note_name}♭ at measure {measure_num} - needs courtesy")
                elif alter_value == 0 and history['first_natural'] is None:
                    history['first_natural'] = measure_num
                    # Naturals don't need courtesy on first encounter in C Major
                
                # Track written accidentals (visible symbols)
                if accidental_match:
                    accidental_type = accidental_match.group(1)
                    print(f"    Written {accidental_type} on {note_name} at measure {measure_num}")
                    history['last_written_accidental'] = measure_num
        
        # Second pass: add courtesy accidentals where needed, plus check for post-written-accidental cases
        processed_notes = set()  # Track which notes have been processed to avoid duplicates
        
        for match in re.finditer(measure_pattern, content, re.DOTALL):
            measure_num = int(match.group(1))
            measure_content = match.group(2)
            
            # Find all notes with pitch in this measure
            note_pattern = r'<note[^>]*>(.*?)</note>'
            for note_match in re.finditer(note_pattern, measure_content, re.DOTALL):
                note_content = note_match.group(1)
                
                # Check if this note has pitch
                pitch_match = re.search(r'<pitch>(.*?)</pitch>', note_content, re.DOTALL)
                if not pitch_match:
                    continue  # Skip rests
                
                pitch_content = pitch_match.group(1)
                
                # Extract step and alter
                step_match = re.search(r'<step>([A-G])</step>', pitch_content)
                alter_match = re.search(r'<alter>([-]?\d+)</alter>', pitch_content)
                
                if not step_match:
                    continue
                
                note_name = step_match.group(1)
                alter_value = int(alter_match.group(1)) if alter_match else 0
                note_key = f"{note_name}_{measure_num}_{alter_value}"
                
                # Skip if already processed (avoid duplicates)
                if note_key in processed_notes:
                    continue
                processed_notes.add(note_key)
                
                # Check for courtesy after written accidental
                if note_name in note_history:
                    history = note_history[note_name]
                    
                    # Case: First occurrence after written accidental
                    if (history['last_written_accidental'] is not None and 
                        measure_num > history['last_written_accidental'] and
                        measure_num not in history['needs_courtesy']):
                        
                        # This is the first occurrence of this note after a written accidental
                        history['needs_courtesy'].add(measure_num)
                        
                        if alter_value == 0:
                            print(f"    {note_name} natural at measure {measure_num} needs courtesy (first after written accidental)")
                        elif alter_value == 1:
                            print(f"    {note_name}# at measure {measure_num} needs courtesy (first after written accidental)")
                        elif alter_value == -1:
                            print(f"    {note_name}♭ at measure {measure_num} needs courtesy (first after written accidental)")
                        
                        # Clear the written accidental marker so we don't add courtesy repeatedly
                        history['last_written_accidental'] = None

        # Third pass: add courtesy accidentals where needed
        def process_measure_for_courtesy(match):
            nonlocal accidentals_added
            measure_num = int(match.group(1))
            measure_content = match.group(2)
            
            # Track courtesy accidentals already added in this measure to prevent duplicates
            courtesy_added_in_measure = set()
            
            def add_courtesy_to_note(note_match):
                nonlocal accidentals_added
                note_content = note_match.group(1)
                
                # Check if this note already has an accidental
                if '<accidental' in note_content:
                    return note_match.group(0)  # Already has accidental, don't add courtesy
                
                # Check if this note has pitch
                pitch_match = re.search(r'<pitch>(.*?)</pitch>', note_content, re.DOTALL)
                if not pitch_match:
                    return note_match.group(0)  # No pitch (rest, etc.)
                
                pitch_content = pitch_match.group(1)
                
                # Extract step and alter
                step_match = re.search(r'<step>([A-G])</step>', pitch_content)
                alter_match = re.search(r'<alter>([-]?\d+)</alter>', pitch_content)
                
                if not step_match:
                    return note_match.group(0)
                
                note_name = step_match.group(1)
                alter_value = int(alter_match.group(1)) if alter_match else 0
                
                # Check if this note needs courtesy accidental
                if (note_name in note_history and 
                    measure_num in note_history[note_name]['needs_courtesy']):
                    
                    # Check if we already added courtesy for this note in this measure
                    courtesy_key = f"{note_name}_{alter_value}"
                    if courtesy_key in courtesy_added_in_measure:
                        return note_match.group(0)  # Skip - already added in this measure
                    
                    # Mark this note+alteration as processed in this measure
                    courtesy_added_in_measure.add(courtesy_key)
                    
                    # Determine courtesy type
                    if alter_value == 1:
                        courtesy_type = 'sharp'
                        reason = f"pedagogical courtesy for {note_name}#"
                    elif alter_value == -1:
                        courtesy_type = 'flat'
                        reason = f"pedagogical courtesy for {note_name}♭"
                    elif alter_value == 0:
                        courtesy_type = 'natural'
                        reason = f"pedagogical courtesy for {note_name}♮"
                    else:
                        return note_match.group(0)  # Unknown alteration
                    
                    print(f"  Adding courtesy {courtesy_type} for {note_name} in measure {measure_num} ({reason})")
                    
                    # Insert courtesy accidental after the pitch element
                    courtesy_accidental = f'<accidental cautionary="yes">{courtesy_type}</accidental>'
                    
                    # Find where to insert (after </pitch>)
                    pitch_end = note_content.find('</pitch>')
                    if pitch_end != -1:
                        insertion_point = pitch_end + len('</pitch>')
                        new_note_content = (note_content[:insertion_point] + 
                                          '\n        ' + courtesy_accidental + 
                                          note_content[insertion_point:])
                        
                        accidentals_added += 1
                        return f'<note>{new_note_content}</note>'
                
                return note_match.group(0)
            
            # Apply courtesy accidental logic to all notes in measure
            note_pattern = r'<note[^>]*>(.*?)</note>'
            new_measure_content = re.sub(note_pattern, add_courtesy_to_note, measure_content, flags=re.DOTALL)
            
            return f'<measure number="{measure_num}">{new_measure_content}</measure>'
        
        # Apply courtesy accidentals to all measures
        content = re.sub(measure_pattern, process_measure_for_courtesy, content, flags=re.DOTALL)
        
        print(f"  Added {accidentals_added} courtesy accidentals for C Major students")
        self.courtesy_accidentals_added = accidentals_added
        return content
    
    def add_brass_fingerings_to_accidentals(self, content, source_instrument):
        """
        Add brass instrument fingerings to ALL notes with accidentals (written and courtesy).
        
        Supports:
        - Bb Trumpet: Valve combinations (0, 1, 2, 12, 13, 23, 123)
        - F Horn: Valve combinations with horn-specific fingerings
        
        This helps brass students by showing valve combinations for any sharp, flat, 
        or natural that appears in the music, including courtesy accidentals.
        
        Args:
            content: MusicXML content string
            source_instrument: Instrument type ('bb_trumpet' or 'f_horn')
            
        Returns:
            Modified content with brass fingerings added to accidental notes
        """
        fingerings_added = 0
        
        # Select appropriate fingering chart and instrument name
        if source_instrument == 'bb_trumpet':
            fingering_chart = self.BB_TRUMPET_FINGERINGS
            instrument_name = "trumpet"
        elif source_instrument == 'f_horn':
            fingering_chart = self.F_HORN_FINGERINGS
            instrument_name = "horn"
        else:
            print(f"  No fingering chart available for {source_instrument}")
            return content
        
        print(f"  Adding {instrument_name} fingerings to all accidental notes...")
        
        # Find all notes with accidentals (both written and courtesy)
        note_pattern = r'<note[^>]*>(.*?)</note>'
        
        def add_trumpet_fingering_to_note(match):
            nonlocal fingerings_added
            note_content = match.group(1)
            
            # Check if this note already has fingerings
            if '<fingering>' in note_content:
                return match.group(0)  # Skip if already has fingering
            
            # Check for accidental marking (both written and courtesy)
            accidental_match = re.search(r'<accidental[^>]*>([^<]+)</accidental>', note_content)
            
            # Only add fingerings to notes that have VISIBLE accidentals
            # This includes both written accidentals and courtesy accidentals
            if not accidental_match:
                return match.group(0)  # No visible accidental, no fingering needed
            
            pitch_match = re.search(r'<pitch>(.*?)</pitch>', note_content, re.DOTALL)
            if not pitch_match:
                return match.group(0)  # No pitch (rest, etc.)
            
            pitch_content = pitch_match.group(1)
            
            # Extract step, octave, and alter
            step_match = re.search(r'<step>([A-G])</step>', pitch_content)
            octave_match = re.search(r'<octave>(\d+)</octave>', pitch_content)
            alter_match = re.search(r'<alter>([-]?\d+)</alter>', pitch_content)
            
            if not step_match or not octave_match:
                return match.group(0)
            
            step = step_match.group(1)
            octave = int(octave_match.group(1))
            alter = int(alter_match.group(1)) if alter_match else 0
            
            # Look up fingering in appropriate chart
            fingering_key = (step, alter, octave)
            if fingering_key in fingering_chart:
                fingering_info = fingering_chart[fingering_key]
                fingering_text = fingering_info['fingering']
                
                # Create technical notation for brass fingering
                technical_notation = f'''        <notations>
          <technical>
            <fingering placement="above">{fingering_text}</fingering>
          </technical>
        </notations>'''
                
                # Find where to insert fingering (after </pitch> but before any existing notations)
                pitch_end = note_content.find('</pitch>')
                if pitch_end != -1:
                    insertion_point = pitch_end + len('</pitch>')
                    
                    # Check if there are already notations - if so, merge with them
                    notations_match = re.search(r'(\s*)<notations>(.*?)</notations>', note_content[insertion_point:], re.DOTALL)
                    if notations_match:
                        # Add to existing notations
                        existing_notations = notations_match.group(2)
                        new_fingering = f'''          <technical>
            <fingering placement="above">{fingering_text}</fingering>
          </technical>'''
                        
                        updated_notations = f'''{notations_match.group(1)}<notations>{existing_notations}{new_fingering}
        </notations>'''
                        
                        new_note_content = (note_content[:insertion_point] + 
                                          re.sub(r'\s*<notations>.*?</notations>', updated_notations, 
                                               note_content[insertion_point:], flags=re.DOTALL))
                    else:
                        # Insert new notations
                        new_note_content = (note_content[:insertion_point] + 
                                          '\n' + technical_notation + 
                                          note_content[insertion_point:])
                    
                    fingerings_added += 1
                    return f'<note>{new_note_content}</note>'
            else:
                # Note is outside normal trumpet range or not in fingering chart
                return match.group(0)
            
            return match.group(0)
        
        # Apply fingerings to all notes with accidentals
        content = re.sub(note_pattern, add_trumpet_fingering_to_note, content, flags=re.DOTALL)
        
        print(f"  Added {fingerings_added} {instrument_name} fingerings to accidental notes")
        self.trumpet_fingerings_added = fingerings_added  # Keep same variable name for compatibility
        return content
    
    def simplify_file(self, input_path, output_path, rules='downbeat', fix_rehearsal='measure_numbers', center_title=False, sync_part_names=None, auto_sync_part_names=False, source_instrument=None, clean_credits=True, remove_multimeasure_rests=False, add_fingerings=False, fingering_style='numbers', skip_rhythm_simplification=False, add_courtesy_accidentals=False, add_courtesy_fingerings=False):
        """
        Simplify a MusicXML file and save the result.
        
        Args:
            input_path: Path to input MusicXML file
            output_path: Path for output file
            rules: Which rule set to apply ('downbeat', etc.)
            fix_rehearsal: Rehearsal mark processing ('measure_numbers', 'letters', or None)
            center_title: Whether to center the title
            sync_part_names: Part name to sync across all references (or None)
            auto_sync_part_names: Whether to auto-detect and sync existing part names
            clean_credits: Whether to clean up credit text
            remove_multimeasure_rests: Whether to convert multi-measure rests
            skip_rhythm_simplification: Whether to skip rhythm changes and only apply OMR fixes
        """
        
        # Read input file
        try:
            with open(input_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            print(f"Error reading input file: {e}")
            return False
        
        # Apply rules (skip rhythm simplification if requested)
        if skip_rhythm_simplification:
            print("Skipping rhythm simplification - preserving original note values")
            simplified_content = content
            self.rules_applied.append('omr_correction_only')
        elif rules == 'downbeat':
            simplified_content = self.apply_downbeat_rules(content)
            self.rules_applied.append('downbeat_simplification')
        else:
            print(f"Unknown rule set: {rules}")
            return False
        
        # Transpose high notes for beginner accessibility (skip if preserving original)
        if not skip_rhythm_simplification:
            print(f"\nTransposing high notes for beginners...")
            simplified_content = self.transpose_high_notes_for_beginners(simplified_content)
        else:
            print(f"\nSkipping high note transposition - preserving original pitches")
        
        # Add saxophone fingerings if requested (after transposition to match final pitches)
        if add_fingerings and source_instrument == 'eb_alto_sax' and not skip_rhythm_simplification:
            print(f"\nAdding saxophone fingerings...")
            simplified_content = self.add_saxophone_fingerings(simplified_content, fingering_style)
        elif add_fingerings and source_instrument != 'eb_alto_sax':
            print(f"\nWarning: Fingering charts are only available for alto saxophone. Skipping fingerings for {source_instrument}.")
        elif add_fingerings and skip_rhythm_simplification:
            print(f"\nSkipping fingering additions - preserving original notation")
        
        # Fix rehearsal marks if requested
        if fix_rehearsal:
            print(f"\nFixing rehearsal marks (mode: {fix_rehearsal})...")
            simplified_content = self.fix_rehearsal_marks(simplified_content, fix_rehearsal)
        
        # Center title if requested
        if center_title:
            print(f"\nCentering title...")
            simplified_content = self.center_title(simplified_content)
        
        # Correct instrument metadata if specified (do this before part name sync)
        if source_instrument:
            print(f"\nCorrecting instrument metadata...")
            # Update part names to match instrument when auto-sync is enabled
            update_parts = auto_sync_part_names and not sync_part_names
            simplified_content = self.correct_instrument_metadata(simplified_content, source_instrument, update_parts)
            self.rules_applied.append(f'instrument_correction_{source_instrument}')
        
        # Sync part names if requested or auto-sync (after instrument correction)
        if sync_part_names:
            print(f"\nSynchronizing part names...")
            simplified_content = self.sync_part_names(simplified_content, sync_part_names)
            if self.rehearsal_marks_fixed > 0:
                self.rules_applied.append(f'rehearsal_marks_{fix_rehearsal}')
        elif auto_sync_part_names and not source_instrument:
            # Only do auto-sync if we didn't already update part names during instrument correction
            print(f"\nAuto-synchronizing part names...")
            detected_name = self.detect_part_name(simplified_content)
            if detected_name:
                simplified_content = self.sync_part_names(simplified_content, detected_name)
                self.rules_applied.append('auto_sync_part_names')
            else:
                print("  No part name detected for auto-sync")
        
        # Add title from filename if missing (before credit cleaning to avoid duplication)
        print(f"\nAdding title from filename...")
        simplified_content = self.add_title_from_filename(simplified_content, input_path)
        
        # Clean up credit text formatting if requested
        if clean_credits:
            print(f"\nCleaning credit text...")
            simplified_content = self.clean_credit_text(simplified_content)
        
        # Remove multi-measure rests if requested
        if remove_multimeasure_rests:
            print(f"\nRemoving multi-measure rests...")
            simplified_content = self.remove_multimeasure_rests(simplified_content)
        
        # Add courtesy accidentals if requested
        if add_courtesy_accidentals:
            print(f"\nAdding courtesy accidentals...")
            simplified_content = self.add_courtesy_accidentals(simplified_content)
        
        # Add courtesy fingerings if requested (for brass instruments)
        if add_courtesy_fingerings and source_instrument in ['bb_trumpet', 'f_horn']:
            print(f"\nAdding courtesy fingerings...")
            simplified_content = self.add_brass_fingerings_to_accidentals(simplified_content, source_instrument)
        
        # Update title/metadata to indicate processing type
        # Only auto-update part name if we're not using custom part names or auto-sync
        if not sync_part_names and not auto_sync_part_names:
            if skip_rhythm_simplification:
                simplified_content = self._update_metadata_omr(simplified_content)
            else:
                simplified_content = self._update_metadata(simplified_content)
        else:
            # Just update the software credit, not the part name
            if skip_rhythm_simplification:
                simplified_content = self._update_software_credit_omr(simplified_content)
            else:
                simplified_content = self._update_software_credit(simplified_content)
        
        # Write output file
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(simplified_content)
        except Exception as e:
            print(f"Error writing output file: {e}")
            return False
        
        return True
    
    def transpose_high_notes_for_beginners(self, content):
        """
        Transpose notes that are too high for beginner alto sax players.
        
        For alto saxophone, the register break happens at D5. Notes D5 and above
        require the octave key and are challenging for beginners. This function
        transposes such notes down by one octave to make them more accessible.
        
        Safe beginner range: Bb3 to C5 (no octave key needed)
        Advanced range: D5 and above (octave key required - transpose down)
        """
        print("Transposing high notes for beginner accessibility...")
        
        notes_transposed = 0
        
        def transpose_pitch_block(match):
            nonlocal notes_transposed
            
            pitch_content = match.group(1)
            
            # Extract step, octave, and alter using regex
            step_match = re.search(r'<step>([A-G])</step>', pitch_content)
            octave_match = re.search(r'<octave>(\d+)</octave>', pitch_content)
            alter_match = re.search(r'<alter>([-]?\d+)</alter>', pitch_content)
            
            if not step_match or not octave_match:
                return match.group(0)  # Return unchanged if we can't parse
            
            step = step_match.group(1)
            octave = int(octave_match.group(1))
            alter = int(alter_match.group(1)) if alter_match else None
            
            # Determine if note needs transposition (C#5 and above)
            # C5 is the highest note beginners should play without octave key
            needs_transposition = False
            if octave > 5:
                needs_transposition = True
            elif octave == 5 and step in ['D', 'E', 'F', 'G', 'A', 'B']:
                needs_transposition = True
            elif octave == 5 and step == 'C' and alter == 1:  # C#5 should also be transposed
                needs_transposition = True
            
            # Transpose if needed
            if needs_transposition:
                new_octave = octave - 1
                notes_transposed += 1
                
                # Replace the octave value in the pitch content
                new_pitch_content = re.sub(r'<octave>\d+</octave>', f'<octave>{new_octave}</octave>', pitch_content)
                
                alter_str = f"#{alter}" if alter == 1 else f"b{-alter}" if alter == -1 else ""
                print(f"  Transposed {step}{alter_str}{octave} -> {step}{alter_str}{new_octave}")
                
                return f'<pitch>{new_pitch_content}</pitch>'
            else:
                return match.group(0)  # Return unchanged
        
        # Use regex to find and process all pitch blocks
        result_content = re.sub(r'<pitch>(.*?)</pitch>', transpose_pitch_block, content, flags=re.DOTALL)
        
        if notes_transposed > 0:
            print(f"  Transposed {notes_transposed} high notes down one octave for beginner accessibility")
        else:
            print(f"  No high notes found that needed transposition")
        
        return result_content
    
    def add_saxophone_fingerings(self, content, fingering_style="numbers"):
        """
        Add saxophone fingering notations to notes in MusicXML content.
        Only adds fingerings for unfamiliar or challenging notes that beginners would need help with.
        
        Args:
            content: MusicXML content string
            fingering_style: "numbers" for simple fingering numbers, "holes" for hole diagrams, "both" for both
        
        Returns:
            Modified MusicXML content with fingering notations added
        """
        print(f"Adding saxophone fingerings (style: {fingering_style})...")
        
        # Define which notes are familiar to beginners (don't need fingerings)
        familiar_notes = {
            # First register notes - familiar to beginners (no fingerings needed)
            ('B', -1, 3),  # Bb3 - low Bb
            ('B', 0, 3),   # B3 - low B  
            ('C', 0, 4),   # C4 - low C
            ('D', 0, 4),   # D4 - low D
            ('E', 0, 4),   # E4 - low E
            ('F', 0, 4),   # F4 - low F
            ('G', 0, 4),   # G4 - low G (thumb only)
            ('A', 0, 4),   # A4 - first note learned
            ('B', 0, 4),   # B4 - second note learned  
            ('C', 0, 5),   # C5 - middle space (LH finger 2 only)
            # Only show fingerings for accidentals and difficult keys
        }
        
        fingerings_added = 0
        
        def add_fingering_to_note(match):
            nonlocal fingerings_added
            
            note_opening_tag = match.group(0)[:match.group(0).find('>')+1]  # Extract <note ...>
            note_content = match.group(1)
            
            # Check if this note already has notations or fingerings
            if '<technical>' in note_content and '<fingering>' in note_content:
                return match.group(0)  # Skip if already has fingerings
            
            # Extract pitch information
            pitch_match = re.search(r'<pitch>(.*?)</pitch>', note_content, re.DOTALL)
            if not pitch_match:
                return match.group(0)  # Skip if no pitch (rests, etc.)
            
            pitch_content = pitch_match.group(1)
            
            # Extract step, octave, and alter
            step_match = re.search(r'<step>([A-G])</step>', pitch_content)
            octave_match = re.search(r'<octave>(\d+)</octave>', pitch_content)
            alter_match = re.search(r'<alter>([-]?\d+)</alter>', pitch_content)
            
            if not step_match or not octave_match:
                return match.group(0)  # Skip if can't parse pitch
            
            step = step_match.group(1)
            octave = int(octave_match.group(1))
            alter = int(alter_match.group(1)) if alter_match else 0
            
            # Look up fingering in database
            fingering_key = (step, alter, octave)
            if fingering_key not in self.ALTO_SAX_FINGERINGS:
                return match.group(0)  # Skip if no fingering available
            
            # Skip familiar notes that beginners already know
            if fingering_key in familiar_notes:
                return match.group(0)  # Skip fingering for familiar notes
            
            fingering_data = self.ALTO_SAX_FINGERINGS[fingering_key]
            
            # Build fingering notation XML
            fingering_xml = ""
            
            if fingering_style in ["numbers", "both"]:
                # Handle empty fingering strings (like G4 which is thumb-only)
                fingering_text = fingering_data["fingering"] if fingering_data["fingering"] else "Th"
                
                # Split fingering into individual components for vertical stacking
                if fingering_text == "Th":
                    fingering_xml += f'        <fingering>T</fingering>\n'
                else:
                    # Split on spaces to separate left hand, right hand, and special keys
                    parts = fingering_text.split()
                    
                    # Collect all fingering elements first, then reverse for bottom-to-top display
                    fingering_elements = []
                    
                    # Process in order: left hand first, then right hand, then special keys
                    for part_idx, part in enumerate(parts):
                        if part == "Oct":
                            fingering_elements.append('8va')
                        elif part == "LowC":
                            fingering_elements.append('C')
                        else:
                            # Split into individual digits and characters
                            for char in part:
                                if char.isdigit():
                                    fingering_elements.append(char)
                                elif char == 'C':
                                    # C key (low Bb)
                                    fingering_elements.append('C')
                    
                    # Reverse the order so they display top-to-bottom in music notation software
                    fingering_elements.reverse()
                    
                    # Add to XML in reversed order
                    for element in fingering_elements:
                        fingering_xml += f'        <fingering>{element}</fingering>\n'
            
            if fingering_style in ["holes", "both"]:
                # Add proper MusicXML hole elements for woodwind fingering
                hole_names = ["LH-Thumb", "LH-1", "LH-2", "LH-3", "RH-1", "RH-2", "RH-3", "RH-4", "Octave-Key"]
                
                for i, (hole_name, is_closed) in enumerate(zip(hole_names, fingering_data["holes"])):
                    fingering_xml += f'        <hole>\n'
                    fingering_xml += f'          <hole-closed>{"yes" if is_closed else "no"}</hole-closed>\n'
                    fingering_xml += f'          <hole-shape>circle</hole-shape>\n'
                    fingering_xml += f'        </hole>\n'
            
            # Check if note already has notations section
            if '<notations>' in note_content:
                # Add to existing notations
                if '<technical>' in note_content:
                    # Add to existing technical section
                    technical_insertion = re.sub(
                        r'(<technical[^>]*>)',
                        r'\1\n' + fingering_xml,
                        note_content
                    )
                else:
                    # Add new technical section to existing notations
                    technical_section = f'      <technical>\n{fingering_xml}      </technical>\n'
                    technical_insertion = re.sub(
                        r'(<notations[^>]*>)',
                        r'\1\n' + technical_section,
                        note_content
                    )
            else:
                # Create new notations section
                technical_section = f'      <technical>\n{fingering_xml}      </technical>'
                notations_section = f'    <notations>\n{technical_section}\n    </notations>'
                
                # Insert before closing </note> tag
                technical_insertion = re.sub(
                    r'(.*)(  </note>)',
                    r'\1' + notations_section + r'\n\2',
                    note_content,
                    flags=re.DOTALL
                )
            
            fingerings_added += 1
            
            # Create note name for logging
            alter_str = "#" if alter == 1 else "b" if alter == -1 else ""
            note_name = f"{step}{alter_str}{octave}"
            fingering_display = fingering_data["fingering"] if fingering_data["fingering"] else "Th"
            
            print(f"  Added fingering for {note_name}: {fingering_display}")
            
            return f'{note_opening_tag}{technical_insertion}</note>'
        
        # Use regex to find and process all note blocks with pitches
        result_content = re.sub(r'<note[^>]*>(.*?)</note>', add_fingering_to_note, content, flags=re.DOTALL)
        
        if fingerings_added > 0:
            print(f"  Added fingerings to {fingerings_added} notes")
        else:
            print(f"  No applicable notes found for fingering notation")
        
        return result_content
    
    def add_title_from_filename(self, content, input_path):
        """Add a main title credit extracted from the filename if no title exists."""
        from pathlib import Path
        
        # Extract filename and clean it up
        filename = Path(input_path).stem  # Gets filename without extension
        
        # Remove common prefixes/suffixes and clean up the title
        title = filename
        
        # Remove leading numbers and dots (e.g., "3. " from "3. Driving Home for Christmas Part 2 Sax")
        title = re.sub(r'^\d+\.\s*', '', title)
        
        # Remove part/instrument info at the end (e.g., "Part 2 Sax", "Part 3 Alto Sax Eb")
        title = re.sub(r'\s+Part\s+\d+.*$', '', title, flags=re.IGNORECASE)
        
        # Remove standalone instrument names at the end
        title = re.sub(r'\s+(Sax|Saxophone|Trumpet|Clarinet|Horn|Flute|Piano)(\s+\w+)*$', '', title, flags=re.IGNORECASE)
        
        # Clean up any extra whitespace
        title = title.strip()
        
        if not title:
            return content  # Don't add empty title
            
        # Check if a main title already exists by looking for key words from the title
        title_words = title.upper().split()
        # Check if the majority of title words are already present in existing credits
        existing_credits = re.findall(r'<credit-words[^>]*>([^<]+)</credit-words>', content)
        for credit_text in existing_credits:
            credit_upper = credit_text.upper()
            matching_words = sum(1 for word in title_words if word in credit_upper)
            # If most of the title words are found in an existing credit, skip adding
            if matching_words >= len(title_words) * 0.7:  # 70% match threshold
                print(f"  Main title '{title}' similar to existing credit '{credit_text.strip()}', skipping")
                return content
            
        # Find the first credit element to insert before it
        first_credit_match = re.search(r'(\s*)<credit page="1">', content)
        if not first_credit_match:
            print(f"  No credits section found, cannot add title")
            return content
            
        indent = first_credit_match.group(1)  # Preserve indentation
        
        # Create the title credit matching Last Christmas formatting (centered, default font)
        title_credit = f'''{indent}<credit page="1">
{indent}  <credit-words default-x="616.9354838709677" default-y="1357.258064516129" justify="center" valign="top">{title.upper()}</credit-words>
{indent}  </credit>
{indent}'''
        
        # Insert the title credit before the first existing credit
        content = content.replace(first_credit_match.group(0), title_credit + first_credit_match.group(0))
        
        print(f"  Added main title: '{title}'")
        return content
    
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
    
    def _update_metadata_omr(self, content):
        """Update the file metadata to indicate it's been processed for OMR correction."""
        # Update part name
        content = re.sub(
            r'(<miscellaneous-field name="partName">.*?)(</miscellaneous-field>)',
            r'\1 - OMR Corrected\2',
            content
        )
        
        # Update software credit
        content = self._update_software_credit_omr(content)
        
        return content
    
    def _update_software_credit_omr(self, content):
        """Update just the software credit to indicate OMR correction processing."""
        content = re.sub(
            r'(<software>.*?)(</software>)',
            r'\1 - OMR Corrected by MusicXML Simplifier\2',
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
        print(f"Courtesy accidentals added: {self.courtesy_accidentals_added}")
        print(f"Courtesy fingerings added: {self.trumpet_fingerings_added}")
        print(f"Rules applied: {', '.join(self.rules_applied)}")
        print("=== End Summary ===\n")


def get_instrument_selection():
    """
    Interactive prompt for source instrument selection.
    Returns the selected instrument key.
    """
    instruments = {
        '1': ('bb_trumpet', 'Bb Trumpet'),
        '2': ('bb_clarinet', 'Bb Clarinet'), 
        '3': ('f_horn', 'F French Horn'),
        '4': ('eb_alto_sax', 'Eb Alto Saxophone'),
        '5': ('flute', 'Flute'),
        '6': ('concert_pitch', 'Concert Pitch (C instruments like Piano)')
    }
    
    print("\n🎵 Source Instrument Selection")
    print("=" * 50)
    print("Please select the original instrument this music was written for:")
    print("(This corrects PDF→MusicXML conversion inconsistencies)")
    print()
    
    for key, (instrument_key, name) in instruments.items():
        print(f"  {key}. {name}")
    
    print()
    while True:
        try:
            choice = input("Enter your choice (1-6): ").strip()
            if choice in instruments:
                instrument_key, name = instruments[choice]
                print(f"Selected: {name}")
                print()
                return instrument_key
            else:
                print("Invalid choice. Please enter 1, 2, 3, 4, 5, or 6.")
        except (EOFError, KeyboardInterrupt):
            print("\nOperation cancelled.")
            return None


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
    parser.add_argument('--auto-sync-part-names', action='store_true',
                       help='Auto-detect and synchronize existing part names for consistency (default in batch mode)')
    parser.add_argument('--source-instrument', type=str, 
                       choices=['bb_trumpet', 'concert_pitch', 'eb_alto_sax', 'f_horn', 'bb_clarinet', 'flute'],
                       help='Correct instrument metadata to match the actual source instrument. If not specified, you will be prompted to select.')
    parser.add_argument('--no-clean-credits', action='store_true',
                       help='Skip cleaning up multi-line credit text (credit cleaning is enabled by default)')
    parser.add_argument('--remove-multimeasure-rests', action='store_true',
                       help='Convert multi-measure rests into individual measure rests for easier counting')
    parser.add_argument('--verbose', '-v', action='store_true',
                       help='Print detailed progress information')
    parser.add_argument('--add-fingerings', action='store_true',
                       help='Add saxophone fingering notations to notes (only for alto sax)')
    parser.add_argument('--fingering-style', default='numbers',
                       choices=['numbers', 'holes', 'both'],
                       help='Style of fingering notation: numbers (simple), holes (diagram), or both')
    parser.add_argument('--skip-rhythm-simplification', action='store_true',
                       help='Skip rhythm simplification and high note transposition, only apply OMR corrections (instrument metadata, titles, credits, part sync)')
    parser.add_argument('--add-courtesy-accidentals', action='store_true',
                       help='Add courtesy accidentals after bar lines and octave changes for clarity')
    parser.add_argument('--add-courtesy-fingerings', action='store_true',
                       help='Add brass fingerings to all accidental notes (trumpet and horn supported)')
    
    args = parser.parse_args()
    
    # Validate input file
    input_path = Path(args.input)
    if not input_path.exists():
        print(f"Error: Input file '{args.input}' not found")
        sys.exit(1)
    
    if not input_path.suffix.lower() in ['.musicxml', '.xml']:
        print(f"Warning: Input file doesn't have .musicxml or .xml extension")
    
    # Handle source instrument selection (now required)
    source_instrument = args.source_instrument
    if not source_instrument:
        source_instrument = get_instrument_selection()
        if not source_instrument:
            print("❌ Instrument selection is required. Exiting.")
            sys.exit(1)
    
    # Create simplifier and process file
    simplifier = MusicXMLSimplifier()
    
    print(f"Simplifying '{args.input}' -> '{args.output}'")
    print(f"Using rule set: {args.rules}")
    if args.rehearsal != 'none':
        print(f"Rehearsal mark mode: {args.rehearsal}")
    if args.center_title:
        print(f"Title centering: enabled")
    if args.sync_part_names:
        print(f"Part name sync: '{args.sync_part_names}'")
    if args.auto_sync_part_names:
        print(f"Auto-sync part names: enabled")
    
    rehearsal_mode = None if args.rehearsal == 'none' else args.rehearsal
    clean_credits = not args.no_clean_credits  # Clean credits by default, disable with --no-clean-credits
    success = simplifier.simplify_file(args.input, args.output, args.rules, rehearsal_mode, args.center_title, args.sync_part_names, args.auto_sync_part_names, source_instrument, clean_credits, args.remove_multimeasure_rests, args.add_fingerings, args.fingering_style, args.skip_rhythm_simplification, args.add_courtesy_accidentals, args.add_courtesy_fingerings)
    
    if success:
        print("SUCCESS: Simplification completed successfully!")
        simplifier.print_summary()
    else:
        print("ERROR: Simplification failed!")
        sys.exit(1)


if __name__ == '__main__':
    main()