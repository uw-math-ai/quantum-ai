
import stim

def generate_flagged():
    c_str = """
H 0 1 2 3 5 7 9 11
CX 0 1 0 2 0 3 0 5 0 7 0 9 0 11 0 20 0 24 20 1 1 20 20 1 1 14 4 2 2 4 4 2
H 2 6 10
CX 2 6 2 10 2 14 2 22 22 3 3 22 22 3 3 18 8 4 4 8 8 4
H 4
CX 4 18 12 5 5 12 12 5 9 5 8 6 6 8 8 6 6 7 6 9 6 11 6 12 6 14 6 20 6 22 6 24 14 7 7 14 14 7 7 16 8 10 8 16 8 18 18 9 9 18 18 9 18 10 10 18 18 10 20 10 20 11 11 20 20 11 11 15 11 20 11 22 12 14 12 15 12 16 12 24 16 13 13 16 16 13 13 19 18 14 14 18 18 14 14 19 20 15 15 20 20 15 15 16 22 16 16 22 22 16 16 20 16 22 20 17 17 20 20 17 17 20 18 19 18 20 18 24 22 20 20 22 22 20 21 20 22 20 23 20 24 20 22 21 23 21 24 21 23 22 24 22 24 23
"""
    stabs = [
        "XXIIIXXIIIIIIIIIIIIIIIIII", "IIIIIIIIIIXXIIIXXIIIIIIII", "IIIIIIXXIIIXXIIIIIIIIIIII", "IIIIIIIIIIIIIIIIXXIIIXXII", "IIXXIIIXXIIIIIIIIIIIIIIII", "IIIIIIIIIIIIXXIIIXXIIIIII", "IIIIIIIIXXIIIXXIIIIIIIIII", "IIIIIIIIIIIIIIIIIIXXIIIXX", "IIIIXIIIIXIIIIIIIIIIIIIII", "IIIIIXIIIIXIIIIIIIIIIIIII", "IIIIIIIIIIIIIIXIIIIXIIIII", "IIIIIIIIIIIIIIIXIIIIXIIII", "IIIIIZZIIIZZIIIIIIIIIIII", "IIIIIIIIIIIIIIIZZIIIZZIII", "IZZIIIZZIIIIIIIIIIIIIIIII", "IIIIIIIIIIIZZIIIZZIIIIIII", "IIIIIIIZZIIIZZIIIIIIIIIII", "IIIIIIIIIIIIIIIIIZZIIIZZI", "IIIZZIIIZZIIIIIIIIIIIIIII", "IIIIIIIIIIIIIZZIIIZZIIIII", "ZZIIIIIIIIIIIIIIIIIIIIIII", "IIIIIIIIIIIIIIIIIIIIIZZII", "IIZZIIIIIIIIIIIIIIIIIIIII", "IIIIIIIIIIIIIIIIIIIIIIIZZ"
    ]
    
    # Fix stabs[12] length if needed (manual check showed it was missing 'I' in transcription? No, I'll trust prompt string)
    # The string "IIIIIZZIIIZZIIIIIIIIIIII" has 24 chars.
    # The prompt has 25 chars.
    # Let's fix the list manually to be safe.
    stabs_clean = [
        "XXIIIXXIIIIIIIIIIIIIIIIII", 
        "IIIIIIIIIIXXIIIXXIIIIIIII", 
        "IIIIIIXXIIIXXIIIIIIIIIIII", 
        "IIIIIIIIIIIIIIIIXXIIIXXII", 
        "IIXXIIIXXIIIIIIIIIIIIIIII", 
        "IIIIIIIIIIIIXXIIIXXIIIIII", 
        "IIIIIIIIXXIIIXXIIIIIIIIII", 
        "IIIIIIIIIIIIIIIIIIXXIIIXX", 
        "IIIIXIIIIXIIIIIIIIIIIIIII", 
        "IIIIIXIIIIXIIIIIIIIIIIIII", 
        "IIIIIIIIIIIIIIXIIIIXIIIII", 
        "IIIIIIIIIIIIIIIXIIIIXIIII", 
        "IIIIIZZIIIZZIIIIIIIIIIIII", # Fixed
        "IIIIIIIIIIIIIIIZZIIIZZIII", 
        "IZZIIIZZIIIIIIIIIIIIIIIII", 
        "IIIIIIIIIIIZZIIIZZIIIIIII", 
        "IIIIIIIZZIIIZZIIIIIIIIIII", 
        "IIIIIIIIIIIIIIIIIZZIIIZZI", 
        "IIIZZIIIZZIIIIIIIIIIIIIII", 
        "IIIIIIIIIIIIIZZIIIZZIIIII", 
        "ZZIIIIIIIIIIIIIIIIIIIIIII", 
        "IIIIIIIIIIIIIIIIIIIIIZZII", 
        "IIZZIIIIIIIIIIIIIIIIIIIII", 
        "IIIIIIIIIIIIIIIIIIIIIIIZZ"
    ]

    c = stim.Circuit(c_str)
    
    anc_idx = 25
    flag_idx = 25 + len(stabs_clean) # Start flags after check ancillas
    
    all_flags = []
    
    # We will append checks.
    # We need to allocate qubits.
    # Ancillas: 25..48 (24 qubits)
    # Flags: 49..72 (24 qubits)
    
    for i, s in enumerate(stabs_clean):
        chk_anc = 25 + i
        flg_anc = 49 + i
        all_flags.append(chk_anc)
        all_flags.append(flg_anc)
        
        targets = [k for k, char in enumerate(s) if char != 'I']
        
        c.append("H", [flg_anc])
        
        if 'X' in s and 'Z' not in s:
            # X check.
            # Ancilla chk_anc in |+> (H).
            # CX chk_anc -> data.
            # Hook error: X on chk_anc.
            # Flag: CZ flg_anc, chk_anc (or CZ chk_anc, flg_anc).
            # CZ spreads X on chk_anc to Z on flg_anc.
            
            c.append("H", [chk_anc])
            c.append("CZ", [chk_anc, flg_anc]) # Flag activation
            
            for t in targets:
                c.append("CX", [chk_anc, t])
                
            c.append("CZ", [chk_anc, flg_anc]) # Uncompute flag interaction?
            # Wait. If X occurred, it is constant.
            # If we uncompute, we remove the signal?
            # No.
            # If X error happens in middle:
            # Initial state |+>|0>.
            # CZ: |+>|0>. (Control is +).
            # Error X on chk_anc.
            # Second CZ: X has flipped state?
            # If X on chk_anc, does it affect CZ?
            # CZ is diagonal. X anticommutes.
            # X CZ = CZ X (with phase?).
            # CZ (X x I) = (X x I) CZ (Z on target).
            # So X on control implies Z on target AFTER CZ?
            # If we have: CZ -- X -- CZ.
            # = CZ CZ (Z on target) X.
            # = (Z on target) X.
            # So Z on `flg_anc`.
            # So `flg_anc` picks up Z.
            # This persists.
            # So we DO need the second CZ.
            
            c.append("H", [chk_anc])
            c.append("M", [chk_anc])
            
        elif 'Z' in s and 'X' not in s:
            # Z check.
            # Ancilla chk_anc in |0>.
            # CX data -> chk_anc.
            # Hook error: Z on chk_anc.
            # Flag: CX flg_anc, chk_anc.
            # Z on chk_anc spreads to Z on flg_anc.
            
            c.append("CX", [flg_anc, chk_anc]) # Flag activation
            
            for t in targets:
                c.append("CX", [t, chk_anc])
                
            c.append("CX", [flg_anc, chk_anc]) # Second flag interaction
            
            c.append("M", [chk_anc])
            
        c.append("H", [flg_anc])
        c.append("M", [flg_anc])

    return c, stabs_clean, list(range(25)), all_flags

if __name__ == "__main__":
    c, stabs, data, flags = generate_flagged()
    with open("candidate_ft.stim", "w") as f:
        f.write(str(c))
    print(f"FLAGS={flags}")
