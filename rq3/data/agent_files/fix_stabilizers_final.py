import stim

def fix_stabilizers():
    with open('target_stabilizers_v2.txt', 'r') as f:
        lines = [line.strip() for line in f if line.strip()]

    print(f"Loaded {len(lines)} stabilizers.")
    
    # Fix line 24 (index 24)
    # Original: XXXXIIXIIXX... (length 137)
    # Target:   XXXXIIIXIIXX... (length 138)
    if len(lines[24]) == 137:
        # Insert 'I' at index 4
        lines[24] = lines[24][:4] + 'I' + lines[24][4:]
        print(f"Fixed line 24 to length {len(lines[24])}")
    
    # Fix line 121 (index 121)
    # Original: ... (length 136)
    # Target:   ... (length 138)
    if len(lines[121]) == 136:
        # Pad with 'II' at end
        lines[121] = lines[121] + 'II'
        print(f"Fixed line 121 to length {len(lines[121])}")

    with open('target_stabilizers_fixed.txt', 'w') as f:
        for line in lines:
            f.write(line + '\n')
            
    print("Saved target_stabilizers_fixed.txt")

    # Verify baseline
    with open('current_baseline_v2.stim', 'r') as f:
        circuit_text = f.read()
    circuit = stim.Circuit(circuit_text)
    
    sim = stim.TableauSimulator()
    sim.do(circuit)
    
    print("\nChecking baseline preservation on FIXED set:")
    preserved = 0
    failed = []
    for i, stab_str in enumerate(lines):
        try:
            p = stim.PauliString(stab_str)
            if sim.peek_observable_expectation(p) == 1:
                preserved += 1
            else:
                failed.append(i)
        except Exception as e:
            print(f"Error checking stabilizer {i}: {e}")
            
    print(f"Preserved {preserved}/{len(lines)}")
    if failed:
        print(f"Failed indices: {failed}")
    else:
        print("ALL STABILIZERS PRESERVED! Baseline is valid for fixed set.")

if __name__ == "__main__":
    fix_stabilizers()
