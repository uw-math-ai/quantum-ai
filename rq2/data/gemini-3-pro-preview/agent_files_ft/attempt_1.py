import sys

orig_circuit_str = """
H 0 1
CX 0 1 0 4
H 2 3
CX 1 2 1 3 1 4 1 5 1 8 1 14 2 4 2 5 2 6 2 9 2 10 4 3 3 4 4 3 3 6 3 10 4 5 4 7 4 8 4 11 4 14 5 6 5 7 5 9 5 11 5 12 6 7 6 12 6 13 7 13 11 8 12 8 13 8 14 8 9 10 12 9 13 9 14 9 12 10 13 10 14 10 12 11 11 12 12 11 11 12 13 11 14 11 13 12 14 12 14 13
"""

stabilizers = [
    "XXXXXXXXIIIIIII", 
    "IXXIXXIIXXIXXII", 
    "IIXXIXXIIXXXIXI", 
    "IIIIXXXXIIIXXXX", 
    "ZZZZIIIIIIIIIII", 
    "IZZIZZIIIIIIIII", 
    "IIZZIZZIIIIIIII", 
    "IIIIZZZZIIIIIII", 
    "IZIIZIIIZIIIZII", 
    "IIZIIZIIIZIZIII", 
    "IIZZIIIIIZZIIII", 
    "IIIIZZIIIIIZZII", 
    "IIIIIZZIIIIZIZI", 
    "IIIIIIZZIIIIIZZ"
]

def generate_circuit():
    # Parse original circuit into individual gates
    circuit_ops = []
    
    lines = orig_circuit_str.strip().split('\n')
    for line in lines:
        parts = line.strip().split()
        if not parts:
            continue
        gate = parts[0]
        qubits = [int(x) for x in parts[1:]]
        
        if gate == "CX":
            # Split into pairs
            for i in range(0, len(qubits), 2):
                circuit_ops.append(f"CX {qubits[i]} {qubits[i+1]}")
        elif gate == "H":
            # Split into singles
            for q in qubits:
                circuit_ops.append(f"H {q}")
        else:
            # Assume single qubit gates or standard format
            circuit_ops.append(line)

    ancilla_start = 15
    current_ancilla = ancilla_start
    
    check_ops = []
    
    # We will simply append check operations using new ancillas
    
    for s_idx, stab in enumerate(stabilizers):
        is_x = 'X' in stab
        is_z = 'Z' in stab
        
        support = [i for i, char in enumerate(stab) if char != 'I']
        ancilla = current_ancilla
        current_ancilla += 1
        
        ops = []
        # Init ancilla (implicit 0)
        
        if is_x and not is_z:
            # Measure X parity: H ancilla, CX ancilla->data, H ancilla
            ops.append(f"H {ancilla}")
            for q in support:
                ops.append(f"CX {ancilla} {q}")
            ops.append(f"H {ancilla}")
        elif is_z and not is_x:
            # Measure Z parity: CX data->ancilla
            # Init 0 is correct for measuring Z parity via CX d->a
            # If d is 1, a flips. Parity accumulation in X basis? No.
            # CX d->a: If d=1, a flips (0->1).
            # If multiple d=1, a flips multiple times.
            # Final state of a is sum(d_i) mod 2. Correct.
            for q in support:
                ops.append(f"CX {q} {ancilla}")
        else:
            # Mixed? Fallback or error
            # For now assume none
            pass
            
        check_ops.extend(ops)

    full_circuit_str = "\n".join(circuit_ops + check_ops)
    
    # Return raw text
    return full_circuit_str

if __name__ == "__main__":
    print(generate_circuit())
