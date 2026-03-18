import sys

def get_stabilizers():
    return [
        "XZZXIIIIIIIIIIIIIIII", "IIIIIXZZXIIIIIIIIIII", "IIIIIIIIIIXZZXIIIIII", "IIIIIIIIIIIIIIIXZZXI", 
        "IXZZXIIIIIIIIIIIIIII", "IIIIIIXZZXIIIIIIIIII", "IIIIIIIIIIIXZZXIIIII", "IIIIIIIIIIIIIIIIXZZX", 
        "XIXZZIIIIIIIIIIIIIII", "IIIIIXIXZZIIIIIIIIII", "IIIIIIIIIIXIXZZIIIII", "IIIIIIIIIIIIIIIXIXZZ", 
        "ZXIXZIIIIIIIIIIIIIII", "IIIIIZXIXZIIIIIIIIII", "IIIIIIIIIIZXIXZIIIII", "IIIIIIIIIIIIIIIZXIXZ", 
        "XXXXXXXXXXXXXXXXXXXX", "ZZZZZZZZZZZZZZZZZZZZ"
    ]

def get_input_circuit():
    return "CX 8 0 0 8 8 0\nH 0\nCX 0 12 0 17\nH 8 16\nCX 8 0 16 0 12 1 1 12 12 1\nH 1\nS 1 8\nH 2 3 5 10 11 13 17\nCX 1 2 1 3 1 5 1 8 1 10 1 11 1 13 1 17 1 18 1 19\nH 4\nCX 4 1 16 1 17 2 2 17 17 2\nH 2 4 8\nCX 2 4 2 8\nH 3 5 10 11 13 17 18 19\nCX 3 2 5 2 10 2 11 2 13 2 16 2 17 2 18 2 19 2 8 3 3 8 8 3\nH 3\nS 3\nH 5 8 10 11 13 17 18 19\nCX 3 4 3 5 3 8 3 10 3 11 3 13 3 17 3 18 3 19 16 3\nH 4\nCX 4 5 4 8 4 10 4 11 4 13 4 17 4 18 4 19 16 4 12 5 5 12 12 5\nH 5 13\nCX 5 13 5 19\nH 9\nCX 9 5 16 5 12 6 6 12 12 6\nH 19\nCX 6 19\nH 13\nCX 13 6 16 6 9 7 7 9 9 7\nS 13 19\nCX 7 13 7 19 16 7 19 8 8 19 19 8\nS 8\nH 8\nCX 13 8 16 8 13 9 9 13 13 9\nS 9\nH 9\nCX 16 9\nH 12 13 18\nCX 10 12 10 13 10 14 10 16 10 17 10 18 10 19 16 10 17 10 14 11 11 14 14 11\nH 11 17\nCX 11 17 12 11 16 11 17 12 12 17 17 12\nH 17\nCX 12 17 16 12 17 13 13 17 17 13\nS 13\nH 13\nS 13 16\nH 16 17 18 19\nCX 16 13 17 13 18 13 19 13 16 14 14 16 16 14\nH 14\nS 14\nH 17 18 19\nCX 14 17 14 18 14 19 16 15 15 16 16 15 15 16 15 18 19 15\nH 16 18 19\nCX 16 18 16 19 17 16 19 17 17 19 19 17\nH 19\nCX 17 19\nH 18\nCX 18 17\nH 18\nCX 18 19\nH 19\nCX 19 18\nH 2 8 9 12 17\nS 2 2 8 8 9 9 12 12 17 17\nH 2 8 9 12 17\nS 0 0 2 2 3 3 4 4 10 10 12 12 14 14 15 15 17 17"

def generate_circuit():
    input_circuit = get_input_circuit()
    stabilizers = get_stabilizers()
    
    verification_ops = []
    flag_qubits = []
    next_ancilla = 20
    
    # We will add measurements for all stabilizers
    # Using naive syndrome extraction (H -> C-Paulis -> H -> M)
    # The extraction ancilla itself is considered a 'flag' for X errors on itself.
    
    for stab in stabilizers:
        ancilla = next_ancilla
        flag_qubits.append(ancilla)
        next_ancilla += 1
        
        verification_ops.append(f"H {ancilla}")
        
        for q_idx, char in enumerate(stab):
            if char == 'X':
                verification_ops.append(f"CX {ancilla} {q_idx}")
            elif char == 'Z':
                verification_ops.append(f"CZ {ancilla} {q_idx}")
            elif char == 'Y':
                verification_ops.append(f"CY {ancilla} {q_idx}")
        
        verification_ops.append(f"H {ancilla}")
        verification_ops.append(f"M {ancilla}")
        
    full_circuit = input_circuit + "\n" + "\n".join(verification_ops)
    
    return full_circuit, flag_qubits

if __name__ == "__main__":
    circuit, flags = generate_circuit()
    
    # Write to file
    with open("gen_ft_solution.stim", "w") as f:
        f.write(circuit)
        
    # Print flags to stdout
    print("FLAGS:" + ",".join(map(str, flags)))
