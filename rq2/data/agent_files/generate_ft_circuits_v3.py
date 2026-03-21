
def generate_circuit():
    # Helper to wrap CX
    # CX c t -> H c H t CX t c H c H t
    def wrap_cx(c, t):
        return f"H {c}\nH {t}\nCX {t} {c}\nH {c}\nH {t}"

    # Original: CX 7 0 0 7 7 0
    # Replaced by wrapped versions
    ops_swap = [
        wrap_cx(7, 0),
        wrap_cx(0, 7),
        wrap_cx(7, 0)
    ]
    
    # Rest of circuit
    base_rest = """H 3
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
    
    final_ops = []
    flag_qubits = []
    
    # Add swap ops
    final_ops.extend(ops_swap)
    
    # Add rest
    final_ops.append(base_rest)
    
    # Add stabilizer checks
    next_ancilla = 15
    for i, stab in enumerate(stabilizers):
        ancilla = next_ancilla
        next_ancilla += 1
        flag_qubits.append(ancilla)
        
        final_ops.append(f"H {ancilla}")
        
        qubits_x = []
        qubits_z = []
        for q_idx, char in enumerate(stab):
            if char == 'X': qubits_x.append(q_idx)
            elif char == 'Z': qubits_z.append(q_idx)
            
        if len(qubits_x) > 0:
            for q in qubits_x:
                final_ops.append(f"CX {ancilla} {q}")
        elif len(qubits_z) > 0:
            for q in qubits_z:
                final_ops.append(f"CZ {ancilla} {q}")
                
        final_ops.append(f"H {ancilla}")
        
    return "\n".join(final_ops), flag_qubits

circuit, flags = generate_circuit()
print(circuit)
print("FLAGS:", flags)
