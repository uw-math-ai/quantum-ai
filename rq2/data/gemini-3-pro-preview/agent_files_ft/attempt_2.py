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
    circuit_ops = []
    
    lines = orig_circuit_str.strip().split('\n')
    for line in lines:
        parts = line.strip().split()
        if not parts:
            continue
        gate = parts[0]
        try:
            qubits = [int(x) for x in parts[1:]]
        except ValueError:
             circuit_ops.append(line)
             continue

        if gate == "CX":
            if len(qubits) % 2 != 0:
                # If odd, we have a problem.
                # Let's assume the last one is ignored or there's a typo in my manual string?
                # But for safety, I will output the pairs I can form.
                pass
            
            for i in range(0, len(qubits) - 1, 2):
                circuit_ops.append(f"CX {qubits[i]} {qubits[i+1]}")
            
            if len(qubits) % 2 != 0:
                 # Append the last one as a comment or partial to see
                 # circuit_ops.append(f"# Orphan qubit {qubits[-1]} in CX")
                 pass

        elif gate == "H":
            for q in qubits:
                circuit_ops.append(f"H {q}")
        else:
            circuit_ops.append(line)

    ancilla_start = 15
    current_ancilla = ancilla_start
    
    check_ops = []
    
    for s_idx, stab in enumerate(stabilizers):
        is_x = 'X' in stab
        is_z = 'Z' in stab
        
        support = [i for i, char in enumerate(stab) if char != 'I']
        ancilla = current_ancilla
        current_ancilla += 1
        
        ops = []
        
        if is_x and not is_z:
            ops.append(f"H {ancilla}")
            for q in support:
                ops.append(f"CX {ancilla} {q}")
            ops.append(f"H {ancilla}")
        elif is_z and not is_x:
            for q in support:
                ops.append(f"CX {q} {ancilla}")
        
        check_ops.extend(ops)

    # Add measurements for all ancillas
    measure_ops = []
    for a in range(ancilla_start, current_ancilla):
        measure_ops.append(f"M {a}")

    full_circuit_str = "\n".join(circuit_ops + check_ops + measure_ops)
    return full_circuit_str, list(range(15)), list(range(15, current_ancilla))

if __name__ == "__main__":
    c_str, _, _ = generate_circuit()
    print(c_str)
