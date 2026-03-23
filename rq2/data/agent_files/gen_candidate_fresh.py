
import stim

def generate():
    # Original circuit
    c_str = """
H 0 1 2 3 5 7 9 11
CX 0 1 0 2 0 3 0 5 0 7 0 9 0 11 0 20 0 24 20 1 1 20 20 1 1 14 4 2 2 4 4 2
H 2 6 10
CX 2 6 2 10 2 14 2 22 22 3 3 22 22 3 3 18 8 4 4 8 8 4
H 4
CX 4 18 12 5 5 12 12 5 9 5 8 6 6 8 8 6 6 7 6 9 6 11 6 12 6 14 6 20 6 22 6 24 14 7 7 14 14 7 7 16 8 10 8 16 8 18 18 9 9 18 18 9 18 10 10 18 18 10 20 10 20 11 11 20 20 11 11 15 11 20 11 22 12 14 12 15 12 16 12 24 16 13 13 16 16 13 13 19 18 14 14 18 18 14 14 19 20 15 15 20 20 15 15 16 22 16 16 22 22 16 16 20 16 22 20 17 17 20 20 17 17 20 18 19 18 20 18 24 22 20 20 22 22 20 21 20 22 20 23 20 24 20 22 21 23 21 24 21 23 22 24 22 24 23
"""
    
    stabs = [
        "XXIIIXXIIIIIIIIIIIIIIIIII", "IIIIIIIIIIXXIIIXXIIIIIIII", "IIIIIIXXIIIXXIIIIIIIIIIII", "IIIIIIIIIIIIIIIIXXIIIXXII", "IIXXIIIXXIIIIIIIIIIIIIIII", "IIIIIIIIIIIIXXIIIXXIIIIII", "IIIIIIIIXXIIIXXIIIIIIIIII", "IIIIIIIIIIIIIIIIIIXXIIIXX", "IIIIXIIIIXIIIIIIIIIIIIIII", "IIIIIXIIIIXIIIIIIIIIIIIII", "IIIIIIIIIIIIIIXIIIIXIIIII", "IIIIIIIIIIIIIIIXIIIIXIIII", "IIIIIZZIIIZZIIIIIIIIIIIII", "IIIIIIIIIIIIIIIZZIIIZZIII", "IZZIIIZZIIIIIIIIIIIIIIIII", "IIIIIIIIIIIZZIIIZZIIIIIII", "IIIIIIIZZIIIZZIIIIIIIIIII", "IIIIIIIIIIIIIIIIIZZIIIZZI", "IIIZZIIIZZIIIIIIIIIIIIIII", "IIIIIIIIIIIIIZZIIIZZIIIII", "ZZIIIIIIIIIIIIIIIIIIIIIII", "IIIIIIIIIIIIIIIIIIIIIZZII", "IIZZIIIIIIIIIIIIIIIIIIIII", "IIIIIIIIIIIIIIIIIIIIIIIZZ"
    ]
    
    c = stim.Circuit(c_str)
    
    # Add checks
    # Start ancilla index at 25
    anc_idx = 25
    
    flag_qubits = []
    
    for s in stabs:
        targets = [i for i, char in enumerate(s) if char != 'I']
        # Determine type
        if 'X' in s and 'Z' not in s:
            # X check
            c.append("H", [anc_idx])
            for t in targets:
                c.append("CX", [anc_idx, t])
            c.append("H", [anc_idx])
            c.append("M", [anc_idx])
            flag_qubits.append(anc_idx)
            anc_idx += 1
            
        elif 'Z' in s and 'X' not in s:
            # Z check
            # For Z check, we measure Z parity.
            # Ancilla (0) -> CX t, anc -> M anc.
            # Wait. CX target, control?
            # If target=data, control=anc.
            # Z on data commutes with control? Yes.
            # X on data flips control? Yes.
            # So `CX anc data` measures X parity (detects Z errors).
            # This is for X stabilizer.
            
            # For Z stabilizer, we want to detect X errors.
            # We need `CX data anc`.
            # X on data flips target (anc).
            # Z on data commutes.
            # So `CX data anc` measures Z parity (detects X errors).
            # Correct.
            
            for t in targets:
                c.append("CX", [t, anc_idx])
            c.append("M", [anc_idx])
            flag_qubits.append(anc_idx)
            anc_idx += 1
            
    return c, stabs, list(range(25)), flag_qubits

if __name__ == "__main__":
    c, stabs, data, flags = generate()
    with open("candidate_ft.stim", "w") as f:
        f.write(str(c))
    print(f"FLAGS={flags}")
