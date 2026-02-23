import stim

def fix_34():
    path = r'data\gemini-3-pro-preview\agent_files\stabilizers_fixed.txt'
    with open(path, 'r') as f:
        lines = [line.strip() for line in f if line.strip()]

    new_lines = list(lines)
    
    # Fix 34
    # Pattern XIIIXIIIIIIIXIX (length 15)
    # Start 121.
    p34 = "XIIIXIIIIIIIXIX"
    s34 = "I"*121 + p34 + "I"*(153 - 121 - len(p34))
    new_lines[34] = s34
    
    out_path = r'data\gemini-3-pro-preview\agent_files\stabilizers_fixed_final.txt'
    with open(out_path, 'w') as f:
        for line in new_lines:
            f.write(line + '\n')
            
    print(f"Fixed line 34 saved to {out_path}")
    
    # Check consistency
    try:
        stabs = [stim.PauliString(line) for line in new_lines]
        tableau = stim.Tableau.from_stabilizers(stabs, allow_redundant=False, allow_underconstrained=True)
        print("Consistency check PASSED!")
        
        circuit = tableau.to_circuit("elimination")
        circ_path = r'data\gemini-3-pro-preview\agent_files\circuit_final.stim'
        with open(circ_path, 'w') as f:
            f.write(str(circuit))
        print(f"Circuit saved to {circ_path}")
        
    except Exception as e:
        print(f"Still inconsistent: {e}")

if __name__ == "__main__":
    fix_34()
