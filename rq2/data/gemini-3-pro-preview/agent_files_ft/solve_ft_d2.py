
def generate_circuit():
    circuit = []
    
    # Original circuit in one block (to avoid reordering concerns/preservation)
    # But wait, original was:
    # H 0
    # CX 0 1 0 2 0 3 0 4 0 5 2 1 3 1 4 1 5 1
    # We should keep this sequence exactly.
    circuit.append("H 0")
    circuit.append("CX 0 1 0 2 0 3 0 4 0 5 2 1 3 1 4 1 5 1")
    
    # Final checks
    # Start ancillas from 6
    ancilla = 6
    
    # Z checks: Z0Z1, Z1Z2, Z2Z3, Z3Z4, Z4Z5
    # Detect X errors.
    z_checks = [(0,1), (1,2), (2,3), (3,4), (4,5)]
    z_ancillas = []
    
    for (u, v) in z_checks:
        circuit.append(f"CX {u} {ancilla} {v} {ancilla}")
        z_ancillas.append(ancilla)
        ancilla += 1
        
    # Final X check: X0X1X2X3X4X5
    # Detects Z errors.
    x_ancilla = ancilla
    circuit.append(f"H {x_ancilla}")
    targets = " ".join([f"{x_ancilla} {i}" for i in range(6)])
    circuit.append(f"CX {targets}")
    circuit.append(f"H {x_ancilla}")
    
    all_ancillas = z_ancillas + [x_ancilla]
    
    return "\n".join(circuit), all_ancillas

if __name__ == "__main__":
    c, ancillas = generate_circuit()
    print(c)
    print(f"ANCILLAS: {ancillas}")
