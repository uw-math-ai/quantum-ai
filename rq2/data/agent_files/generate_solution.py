import stim

def generate_measurement(stabilizer_str, ancilla, flag_qubit=None):
    ops = []
    
    qubits_x = []
    qubits_z = []
    qubits_y = []
    for q, char in enumerate(stabilizer_str):
        if char == "X": qubits_x.append(q)
        elif char == "Z": qubits_z.append(q)
        elif char == "Y": qubits_y.append(q)
        
    weight = len(qubits_x) + len(qubits_z) + len(qubits_y)
    
    is_x_only = (len(qubits_z) == 0 and len(qubits_y) == 0)
    is_z_only = (len(qubits_x) == 0 and len(qubits_y) == 0)
    
    ops.append(f"R {ancilla}")
    ops.append(f"H {ancilla}") 
    
    if flag_qubit is not None:
        ops.append(f"R {flag_qubit}")
        
        if is_x_only:
            # X-only: M is control. X on M spreads. Detect X.
            # Flag in |0>, CNOT M->F.
            ops.append(f"CX {ancilla} {flag_qubit}")
        elif is_z_only:
            # Z-only: M is target. Z on M spreads. Detect Z.
            # Flag in |+>, CNOT F->M.
            ops.append(f"H {flag_qubit}")
            ops.append(f"CX {flag_qubit} {ancilla}")
        else:
            # Mixed. Default to Z detection (common for CSS hooks)
            ops.append(f"H {flag_qubit}")
            ops.append(f"CX {flag_qubit} {ancilla}")

    for q in qubits_x:
        ops.append(f"CX {ancilla} {q}")
        
    for q in qubits_z:
        ops.append(f"CX {q} {ancilla}")
        
    for q in qubits_y:
        ops.append(f"S_DAG {q}")
        ops.append(f"H {q}")
        ops.append(f"CX {q} {ancilla}")
        ops.append(f"H {q}")
        ops.append(f"S {q}")

    if flag_qubit is not None:
        if is_x_only:
            ops.append(f"CX {ancilla} {flag_qubit}")
            ops.append(f"M {flag_qubit}")
        elif is_z_only:
            ops.append(f"CX {flag_qubit} {ancilla}")
            ops.append(f"H {flag_qubit}")
            ops.append(f"M {flag_qubit}")
        else:
            ops.append(f"CX {flag_qubit} {ancilla}")
            ops.append(f"H {flag_qubit}")
            ops.append(f"M {flag_qubit}")

    ops.append(f"H {ancilla}")
    ops.append(f"M {ancilla}")
    
    return ops

def main():
    with open("circuit_input.stim", "r") as f:
        baseline = f.read()
        
    with open("stabilizers.txt", "r") as f:
        stabilizers = [line.strip() for line in f if line.strip()]
        
    for i in range(len(stabilizers)):
        s = stabilizers[i]
        if len(s) < 175:
            stabilizers[i] = s + "I" * (175 - len(s))
        elif len(s) > 175:
            stabilizers[i] = s[:175]

    next_qubit = 175
    ancilla_qubits = []
    
    full_ops = []
    
    for stab in stabilizers:
        is_x = "X" in stab
        is_z = "Z" in stab
        is_y = "Y" in stab
        
        weight = stab.count("X") + stab.count("Z") + stab.count("Y")
        
        flag = None
        if weight >= 7:
            flag = next_qubit
            next_qubit += 1
            ancilla_qubits.append(flag)
            
        ancilla = next_qubit
        next_qubit += 1
        ancilla_qubits.append(ancilla)
        
        meas_ops = generate_measurement(stab, ancilla, flag)
        full_ops.extend(meas_ops)
        
    with open("solution.stim", "w") as f:
        f.write(baseline)
        if not baseline.endswith("\n"):
            f.write("\n")
        f.write("\n".join(full_ops))
        
    with open("ancillas.txt", "w") as f:
        f.write("\n".join(map(str, ancilla_qubits)))
        
    print("Solution generated.")

if __name__ == "__main__":
    main()
