import stim

def apply_fixes():
    path = r'data\gemini-3-pro-preview\agent_files\stabilizers.txt'
    with open(path, 'r') as f:
        lines = [line.strip() for line in f if line.strip()]

    new_lines = list(lines)
    
    # Fix 43
    # Pattern XXXXXIXXIIIIX (length 13), starts at 123
    p43 = "XXXXXIXXIIIIX"
    s43 = "I"*123 + p43 + "I"*(153 - 123 - len(p43))
    new_lines[43] = s43
    
    # Fix 51
    # Pattern XIIXIIIIIXIIX (length 13), starts at 103
    p51 = "XIIXIIIIIXIIX"
    s51 = "I"*103 + p51 + "I"*(153 - 103 - len(p51))
    new_lines[51] = s51
    
    # Fix 109
    # Pattern ZZZZZIZZIIIIZ (length 13), starts at 21
    # Line 108 starts at 4.
    # Line 109 starts at 21. (4 + 17)
    p109 = "ZZZZZIZZIIIIZ"
    s109 = "I"*21 + p109 + "I"*(153 - 21 - len(p109))
    new_lines[109] = s109
    
    out_path = r'data\gemini-3-pro-preview\agent_files\stabilizers_fixed.txt'
    with open(out_path, 'w') as f:
        for line in new_lines:
            f.write(line + '\n')
            
    print(f"Fixed stabilizers saved to {out_path}")
    
    # Now verify consistency
    try:
        stabs = [stim.PauliString(line) for line in new_lines]
        tableau = stim.Tableau.from_stabilizers(stabs, allow_redundant=False, allow_underconstrained=True)
        print("Stabilizers are now consistent!")
        
        # Generate circuit
        circuit = tableau.to_circuit("gaussian")
        circ_path = r'data\gemini-3-pro-preview\agent_files\circuit_fixed.stim'
        with open(circ_path, 'w') as f:
            f.write(str(circuit))
        print(f"Circuit saved to {circ_path}")
        
    except Exception as e:
        print(f"Still inconsistent: {e}")
        # check pairs again
        import subprocess
        # We can run the check_commutation function again here
        pass

if __name__ == "__main__":
    apply_fixes()
