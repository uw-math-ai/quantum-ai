#!/usr/bin/env python3
"""
Extract stabilizer strings from target_stabilizers_153.txt and save to output file.
The file contains 152 stabilizer strings, each of length 153.
"""

import os
import re

def extract_stabilizers():
    """Extract stabilizer strings from the file and verify counts and lengths."""
    
    # Read the source file
    source_file = 'data/agent_files/target_stabilizers_153.txt'
    
    # Read all lines
    with open(source_file, 'r') as f:
        lines = f.readlines()
    
    # Extract stabilizer strings (already clean, no line numbers in file)
    stabilizers = []
    for line in lines:
        line = line.rstrip('\n\r')
        if not line:  # Skip empty lines
            continue
        stabilizers.append(line)
    
    # Verify count
    print(f"Number of stabilizers extracted: {len(stabilizers)}")
    
    # Verify lengths
    if stabilizers:
        lengths = [len(s) for s in stabilizers]
        min_len = min(lengths)
        max_len = max(lengths)
        print(f"Min stabilizer length: {min_len}")
        print(f"Max stabilizer length: {max_len}")
        
        # Show length distribution
        unique_lengths = set(lengths)
        for length in sorted(unique_lengths):
            count = lengths.count(length)
            print(f"  Length {length}: {count} stabilizer(s)")
    
    # Check if we have exactly 152 strings of length 153
    if len(stabilizers) == 152 and all(len(s) == 153 for s in stabilizers):
        print("\n✓ Verification PASSED: 152 strings of length 153")
    else:
        print("\n✗ Verification FAILED:")
        invalid = [(i, len(s)) for i, s in enumerate(stabilizers) if len(s) != 153]
        if invalid:
            print(f"  Found {len(invalid)} strings with incorrect length:")
            for i, length in invalid[:10]:  # Show first 10 errors
                print(f"    String {i}: length {length}")
    
    # Create output directory if needed
    output_dir = 'data/gemini-3-pro-preview/agent_files'
    os.makedirs(output_dir, exist_ok=True)
    
    # Save to output file (one per line)
    output_file = os.path.join(output_dir, 'stabilizers_153_extracted.txt')
    with open(output_file, 'w') as f:
        for stabilizer in stabilizers:
            f.write(stabilizer + '\n')
    
    print(f"\n✓ Saved {len(stabilizers)} stabilizers to: {output_file}")
    
    # Verify the output file was written correctly
    with open(output_file, 'r') as f:
        saved_stabilizers = [line.rstrip('\n') for line in f.readlines()]
    
    if saved_stabilizers == stabilizers:
        print("✓ Output file verification PASSED")
    else:
        print("✗ Output file verification FAILED")
    
    return stabilizers

if __name__ == '__main__':
    stabilizers = extract_stabilizers()
    print(f"\nFirst stabilizer: {stabilizers[0][:50]}..." if stabilizers else "No stabilizers found")
    print(f"Last stabilizer:  {stabilizers[-1][:50]}..." if stabilizers else "No stabilizers found")
