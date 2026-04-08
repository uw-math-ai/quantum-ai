
def generate_circuit():
    base_circuit = """CX 7 0 0 7 7 0
H 3
CX 3 0 4 0 5 0 6 0 8 0 10 0 12 0 13 0 2 1 1 2 2 1
H 1
CX 1 3 1 6 1 9 1 12 1 13 3 2 2 3 3 2 2 6 2 8 2 10 2 12 2 14
H 3
CX 3 5 3 8 3 11 3 12 3 13 3 14 5 4 4 5 5 4 6 4 9 4 10 4 11 4 12 4 6 5 5 6 6 5 8 5 9 5 10 5 13 5 14 5 8 6 6 8 8 6
H 7
CX 7 8 7 9 7 10 7 11 7 12 7 13 7 14 9 8 10 8 11 8 12 8 13 8 14 8"""
    
    stabilizers = [
        "IIIIIIIXXXXXXXX",
        "IIIXXXXIIIIXXXX",
        "IXXIIXXIIXXIIXX",
        "XIXIXIXIXIXIXIX",
        "IIIIIIIZZZZZZZZ",
        "IIIZZZZIIIIZZZZ",
        "IZZIIZZIIZZIIZZ",
        "ZIZIZIZIZIZIZIZ"
    ]
    
    # Check ancilla start index
    # Data qubits are 0-14.
    ancilla_start = 15
    pre_ops = []
    post_ops = []
    flag_qubits = []

    # Add input checks for 0 and 7 at the START
    # 0 check
    ancilla_0 = 23
    flag_qubits.append(ancilla_0)
    pre_ops.append(f"H 0")
    pre_ops.append(f"H {ancilla_0}")
    pre_ops.append(f"CX {ancilla_0} 0")
    pre_ops.append(f"H {ancilla_0}")
    pre_ops.append(f"H 0")

    # 7 check
    ancilla_7 = 24
    flag_qubits.append(ancilla_7)
    pre_ops.append(f"H 7")
    pre_ops.append(f"H {ancilla_7}")
    pre_ops.append(f"CX {ancilla_7} 7")
    pre_ops.append(f"H {ancilla_7}")
    pre_ops.append(f"H 7")

    for i, stab in enumerate(stabilizers):
        ancilla = ancilla_start + i
        flag_qubits.append(ancilla)
        
        # Init is implicit 0, but usually we just start using it.
        # H ancilla
        post_ops.append(f"H {ancilla}")
        
        qubits_x = []
        qubits_z = []
        
        for q_idx, char in enumerate(stab):
            if char == 'X':
                qubits_x.append(q_idx)
            elif char == 'Z':
                qubits_z.append(q_idx)
        
        # If stabilizer is all X (S0-S3)
        if len(qubits_x) > 0 and len(qubits_z) == 0:
            for q in qubits_x:
                post_ops.append(f"CX {ancilla} {q}")
        
        # If stabilizer is all Z (S4-S7)
        elif len(qubits_z) > 0 and len(qubits_x) == 0:
            for q in qubits_z:
                post_ops.append(f"CZ {ancilla} {q}")
                
        # H ancilla
        post_ops.append(f"H {ancilla}")
        
    return "\n".join(pre_ops) + "\n" + base_circuit + "\n" + "\n".join(post_ops), flag_qubits

circuit, flags = generate_circuit()
print(circuit)
print("FLAGS:", flags)
