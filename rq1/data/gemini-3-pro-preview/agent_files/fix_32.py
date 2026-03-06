import stim

def read_stabilizers(filename):
    with open(filename, 'r') as f:
        lines = [line.strip().replace(',', '') for line in f if line.strip()]
    return [stim.PauliString(s) for s in lines]

def main():
    stabilizers = read_stabilizers('data/gemini-3-pro-preview/agent_files/stabilizers_184.txt')
    
    # 32 is the problematic one.
    # It has X on [0, 1, 2, 3, 6, 9, 10, 17]
    # We suspect it should be shifted by -23 from 33, or follow some pattern.
    
    # Let's look at 30 -> 31 -> (wrap?) -> 32?
    # 30: [138, 139, 141, 142, 143, 147, 148, 157]
    # 31: [161, 162, 164, 165, 166, 170, 171, 180]
    
    # The pattern of 30/31 is XX_XXX___XX________X
    # X at 0, 1, 3, 4, 5, 9, 10, 19 (relative to start)
    # 139-138 = 1
    # 141-139 = 2
    # 142-141 = 1
    # 143-142 = 1
    # 147-143 = 4
    # 148-147 = 1
    # 157-148 = 9
    
    # Pattern of 33: XXXX___X__XX______X
    # X at 0, 1, 2, 3, 7, 10, 11, 18 (relative to start)
    # 24-23 = 1
    # 25-24 = 1
    # 26-25 = 1
    # 30-26 = 4
    # 33-30 = 3
    # 34-33 = 1
    # 41-34 = 7
    
    # Pattern of 32: XXXX__X__XX______X
    # X at 0, 1, 2, 3, 6, 9, 10, 17
    # 1-0 = 1
    # 2-1 = 1
    # 3-2 = 1
    # 6-3 = 3
    # 9-6 = 3
    # 10-9 = 1
    # 17-10 = 7
    
    # It seems 32 is shifted version of 33?
    # 33: 23, 24, 25, 26, 30, 33, 34, 41
    # 32:  0,  1,  2,  3,  6,  9, 10, 17
    # Diff: 23, 23, 23, 23, 24, 24, 24, 24.
    
    # It seems 32 is "half-shifted" by 23 and "half-shifted" by 24.
    # If 32 was shifted by 23 from 33 (backwards), it would be:
    # 23-23=0, 24-23=1, 25-23=2, 26-23=3, 30-23=7, 33-23=10, 34-23=11, 41-23=18.
    # So indices: 0, 1, 2, 3, 7, 10, 11, 18.
    # Stabilizer 32 has: 0, 1, 2, 3, 6, 9, 10, 17.
    # The last 4 indices are off by 1.
    
    # Let's try constructing a candidate 32' with indices [0, 1, 2, 3, 7, 10, 11, 18].
    # This corresponds to pattern XXXX___X__XX______X (same as 33).
    
    candidate_indices = [0, 1, 2, 3, 7, 10, 11, 18]
    n_qubits = 184
    new_s32 = stim.PauliString(n_qubits)
    for idx in candidate_indices:
        new_s32[idx] = "X"
        
    print(f"Proposed 32: {new_s32}")
    
    # Check commutativity with the problem set (the Z's).
    anticommuting = [88, 96, 112, 120, 136, 144, 152, 160]
    for i in anticommuting:
        if not new_s32.commutes(stabilizers[i]):
            print(f"Anticommutes with {i}!")
        else:
            print(f"Commutes with {i}")

if __name__ == "__main__":
    main()
