import stim

def check_lengths_and_fix():
    with open(r"C:\Users\anpaz\Repos\quantum-ai\rq1\data\stabilizers_92.txt", "r") as f:
        stabilizers = [line.strip() for line in f if line.strip()]

    # Index 16 is likely the culprit
    # It has "XXXXIIXIIXX..."
    # The others have "XXXXIIIXIIXX..."
    # Let's see if adding an I makes it commute
    
    s16 = stabilizers[16]
    # Try to insert an I somewhere to match the pattern?
    # Or replace II with III? But then we must remove an I from somewhere else to keep length 92?
    
    print(f"Length of s16: {len(s16)}")
    print(f"Pattern of s16: {s16[:20]}")
    
    s17 = stabilizers[17]
    print(f"Length of s17: {len(s17)}")
    print(f"Pattern of s17: {s17[:20]}")

    # It seems s16 is just missing an I.
    # If we add an I, the length becomes 93.
    # But all strings must be length 92.
    # Maybe it's missing an I in the pattern but has an extra I elsewhere?
    
    # Let's try to find a variant of s16 that commutes with everything else.
    # We can try to modify s16 to match the pattern of s17 but shifted?
    # No, s16 starts at index 0. s17 starts at index 23?
    # Wait, looking at the file:
    # 17. XXXXIIXIIXXIIIIIIXIIIIII...
    # 18. IIIIIIIIIIIIIIIIIIIIIIIXXXXIIIXIIXXIIIIIIXII...
    # Ah, 17 is shifted by 0. 18 is shifted by 23.
    # Wait, the structure is usually 4 shifts of a pattern.
    
    # Block 1:
    # 0: IXIIXIIXXXXX...
    # 1: ...XIIXIIXXXXX... (shift 23?)
    # 2: ... (shift 46?)
    # 3: ... (shift 69?)
    
    # Block 3 (indices 16-19):
    # 16: XXXXIIXIIXXIIIIIIX...
    # 17: ...XXXXIIIXIIXXIIIIIIX... (shift 23)
    # 18: ... (shift 46)
    # 19: ... (shift 69)
    
    # So 16 should be the base pattern.
    # 17 is the shifted version.
    # 17 has pattern XXXXIIIXIIXX.
    # 16 has pattern XXXXIIXIIXX.
    # 16 is missing an I.
    
    # If 17 is correct, then 16 should probably be XXXXIIIXIIXX...
    # Let's see if 17 commutes with everything.
    # Wait, check_comm_92.py said 16 anticommutes. It didn't complain about 17.
    # So 17 is probably fine.
    # So 16 should likely be consistent with 17.
    # If I change 16 to match 17's pattern (XXXXIIIXIIXX...), it will be length 93.
    # I need to remove a character to keep it length 92.
    # BUT, if 16 is missing an I, maybe it has an extra I at the end?
    # Or maybe the prompt has a typo and omitted an I, and I should insert it?
    # BUT the string length is 92. If I insert an I, it becomes 93.
    # Maybe I should remove an I from the end?
    
    # Let's construct a candidate s16_new
    # Pattern from s17: "XXXXIIIXIIXXIIIIIIX"
    # s16 current:      "XXXXIIXIIXXIIIIIIX"
    # It seems to be missing the 3rd 'I' in the first group.
    
    # Let's take s17, unshift it (it's shifted by 23), and use that as s16?
    # s17 starts at 23.
    # s17: 23*'I' + "XXXXIIIXIIXXIIIIIIX" + ...
    # Wait, s17 is:
    # IIIIIIIIIIIIIIIIIIIIIIIXXXXIIIXIIXXIIIIIIXIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIII
    # 23 Is, then XXXXIIIXIIXXIIIIIIX...
    
    # So if we shift that back by 23, we get:
    # XXXXIIIXIIXXIIIIIIX... + 23 Is at end?
    
    s17_str = stabilizers[17]
    # Rotate or just shift? usually shift.
    # The pattern seems to be on 92 qubits.
    # If I take the non-I part of s17 and put it at the beginning.
    
    pattern = "XXXXIIIXIIXXIIIIIIX"
    # Check if s17 contains this
    if pattern in s17_str:
        print("Found pattern in s17")
        
    # Construct s16 candidate
    # s16_new = pattern + (92 - len(pattern)) * 'I'
    s16_new = pattern + "I" * (92 - len(pattern))
    
    print(f"Candidate s16: {s16_new}")
    
    # Check if this candidate commutes with the others (specifically the ones 16 failed with)
    # The ones it failed with are 44, 48, 56, 60, 68, 72, 76, 80.
    
    paulis = [stim.PauliString(s) for s in stabilizers]
    s16_pauli = stim.PauliString(s16_new)
    
    failed_indices = [44, 48, 56, 60, 68, 72, 76, 80]
    all_good = True
    for idx in failed_indices:
        if not s16_pauli.commutes(paulis[idx]):
            print(f"Still anticommutes with {idx}")
            all_good = False
            
    if all_good:
        print("Candidate s16 commutes with previously failing stabilizers!")
        
        # Check global commutation
        print("Checking global commutation for s16_new")
        commutes_all = True
        for i, p in enumerate(paulis):
            if i == 16: continue
            if not s16_pauli.commutes(p):
                print(f"Anticommutes with {i}")
                commutes_all = False
        
        if commutes_all:
             print("SUCCESS: s16_new commutes with everything!")
             
             # Save the fixed stabilizers
             stabilizers[16] = s16_new
             with open(r"C:\Users\anpaz\Repos\quantum-ai\rq1\data\stabilizers_92_fixed.txt", "w") as f:
                 for s in stabilizers:
                     f.write(s + "\n")
    else:
        print("Candidate s16 did not fix the issue.")

if __name__ == "__main__":
    check_lengths_and_fix()
