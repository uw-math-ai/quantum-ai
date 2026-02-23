import stim

def generate_with_shift_18():
    # Define blocks by their first line pattern and start index
    # But wait, the start index of the first line of a block might also be shifted?
    # Let's assume the first line of each block is correct?
    # Or maybe the blocks themselves are shifted by 18*9?
    
    # Let's look at the first lines of blocks.
    # Block 1 (Line 0): IIIIIXIIIXIXX... (Start 5)
    # Block 2 (Line 9): IIIIIIIIXIXIIXIX... (Start 8)
    # Block 3 (Line 18): IIIXIIIXIIIIIIXIX... (Start 3)
    # Block 4 (Line 27): IIXIIIXIIIIIIIXIX... (Start 2)
    # Block 5 (Line 36): IIIIXXXXXIXXIIIIX... (Start 4)
    # Block 6 (Line 45): IXIIXIIIIIXIIX... (Start 0 or 1? "IXII..." -> Start 1?)
    # Block 7 (Line 54): IIIIIIIIXXIXIIIXII... (Start 8)
    
    # If the shift within a block is 17, we get anticommutation.
    # If we change it to 18, do we fix it?
    
    # Let's try to generate the full set of stabilizers with shift 18.
    # We need the patterns.
    
    patterns = [
        ("XIIIXIXX", 5), # Line 0
        ("XIXIIXIX", 8), # Line 9
        ("XIIIXIIIIIIXIX", 3), # Line 18
        ("XIIIXIIIIIIIXIX", 2), # Line 27
        ("XXXXXIXXIIIIX", 4), # Line 36
        ("XIIXIIIIIXIIX", 1), # Line 45 (assuming "IXII..." -> I + Pattern)
        ("XXIXIIIXII", 8), # Line 54
        ("XIXXIIIIIIIIIIXII", 0), # Line 63 (Starts with XIXX...)
        ("ZIIIZIZZ", 5), # Line 72
        ("ZIZIIZIZ", 8), # Line 81
        ("ZIIIZIIIIIIZIZ", 3), # Line 90
        ("ZIIIZIIIIIIIZIZ", 2), # Line 99
        ("ZZZZZIZZIIIIZ", 4), # Line 108
        ("ZIIZIIIIIZIIZ", 1), # Line 117
        ("ZZIZIIIZII", 8), # Line 126
        ("ZIZZIIIIIIIIIIZII", 0), # Line 135
        ("XXXIXIXIIIIIIIIIIXXXIXIX", 0), # Line 144
        ("ZZZIZIZIIIIIIIIIIZZZIZIZ", 0) # Line 151? No wait.
    ]
    
    # Last block starts at 144?
    # 153 total lines.
    # 17 blocks of 9 = 153?
    # 17 * 9 = 153.
    # So there are exactly 17 blocks of 9 lines.
    
    # Let's verify my list of patterns.
    # I listed 18 patterns above.
    # If there are 17 blocks, the last one is 16.
    # Let's count again.
    # 0, 9, 18, 27, 36, 45, 54, 63, 72, 81, 90, 99, 108, 117, 126, 135, 144.
    # That's 17 blocks.
    # My list has 18?
    # Ah, the last two in my list: "XXXIXIX..." and "ZZZIZIZ...".
    # Wait, line 144 is "XXXIXIX...".
    # Line 151?
    # 144 + 9 = 153.
    # So the last block is lines 144-152.
    # Is it split?
    # Line 144: XXXIXIX...
    # Line 151: ZZZIZIZ...
    # Maybe the last block is mixed or I miscounted.
    
    # Let's just use the first line of each 9-line chunk as the "seed".
    # Then generate the other 8 lines by shifting 18.
    
    lines = []
    
    # Read the file to get the seeds
    with open(r'data\gemini-3-pro-preview\agent_files\stabilizers_fixed.txt', 'r') as f:
        file_lines = [line.strip() for line in f if line.strip()]
        
    num_blocks = 17
    generated_stabilizers = []
    
    for b in range(num_blocks):
        start_line_idx = b * 9
        seed_line = file_lines[start_line_idx]
        
        # Determine pattern and start index from seed
        # We need to strip leading Is
        first_non_I = -1
        for k, c in enumerate(seed_line):
            if c != 'I':
                first_non_I = k
                break
        
        if first_non_I == -1:
            print(f"Block {b} seed is empty!")
            continue
            
        pattern = seed_line[first_non_I:].rstrip('I')
        start_index = first_non_I
        
        # Generate 9 lines
        for i in range(9):
            pos = start_index + i * 17 # Try 17 first to reproduce file
            # If I use 18, I get the fix?
            
            # Let's try 18.
            pos_18 = start_index + i * 18
            
            # Construct line
            line = "I" * pos_18 + pattern + "I" * (153 - pos_18 - len(pattern))
            # Check length
            if len(line) != 153:
                # If too long, maybe wrap around? Or truncate?
                # Or maybe the pattern goes off the edge?
                # If pos_18 + len > 153, it's invalid.
                pass
            
            generated_stabilizers.append(line)

    # Convert to stim and check consistency
    try:
        stabs = [stim.PauliString(s) for s in generated_stabilizers if len(s) == 153]
        if len(stabs) != 153:
            print(f"Generated {len(stabs)} valid stabilizers (expected 153)")
            
        tableau = stim.Tableau.from_stabilizers(stabs, allow_redundant=False, allow_underconstrained=True)
        print("Success! Shift 18 works.")
        
        circuit = tableau.to_circuit("gaussian")
        with open(r'data\gemini-3-pro-preview\agent_files\circuit_shift18.stim', 'w') as f:
            f.write(str(circuit))
            
    except Exception as e:
        print(f"Shift 18 failed: {e}")

if __name__ == "__main__":
    generate_with_shift_18()
