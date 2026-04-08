import sys

def parse_circuit(circuit_str):
    operations = []
    lines = circuit_str.strip().split('\n')
    for line in lines:
        parts = line.strip().split()
        if not parts: continue
        gate = parts[0]
        if gate.startswith('#'): continue
        qubits = []
        for x in parts[1:]:
            try:
                qubits.append(int(x))
            except ValueError:
                pass
        operations.append((gate, qubits))
    return operations

def analyze_degrees(operations):
    control_counts = {}
    for gate, qubits in operations:
        if gate == "CX":
            for i in range(0, len(qubits), 2):
                c = qubits[i]
                control_counts[c] = control_counts.get(c, 0) + 1
    return control_counts

def generate_ft_circuit(input_path, output_path):
    with open(input_path, 'r') as f:
        content = f.read()
    
    ops = parse_circuit(content)
    degrees = analyze_degrees(ops)
    
    max_idx = 0
    for gate, qubits in ops:
        if qubits:
            max_idx = max(max_idx, max(qubits))
            
    next_idx = max_idx + 1
    new_ops = []
    added_ancillas = []
    
    BUSY_THRESHOLD = 3
    
    for gate, qubits in ops:
        if gate == "H":
            for q in qubits:
                # Check if q is busy
                if degrees.get(q, 0) > BUSY_THRESHOLD:
                    # Apply Z-check gadget
                    # Uses 1 ancilla 'a'
                    a = next_idx
                    next_idx += 1
                    added_ancillas.append(a)
                    
                    # 1. H q
                    new_ops.append(f"H {q}")
                    
                    # 2. Check Z error on q
                    # Prepare a in |+>
                    new_ops.append(f"H {a}")
                    # CX a q (propagates Z from q to a)
                    new_ops.append(f"CX {a} {q}")
                    # Measure a in X (H then measure)
                    new_ops.append(f"H {a}")
                    # Measurement is implicit at end of circuit
                    
                else:
                    new_ops.append(f"H {q}")
        elif gate == "CX":
            q_str = " ".join(str(x) for x in qubits)
            new_ops.append(f"CX {q_str}")
        elif gate == "S":
            q_str = " ".join(str(x) for x in qubits)
            new_ops.append(f"S {q_str}")
        else:
            q_str = " ".join(str(x) for x in qubits)
            new_ops.append(f"{gate} {q_str}")
            
    with open(output_path, 'w') as f:
        for line in new_ops:
            f.write(line + "\n")
            
    print(f"Generated. Ancillas: {added_ancillas}")

if __name__ == "__main__":
    generate_ft_circuit(
        r"C:\Users\anpaz\Repos\quantum-ai\rq2\data\gemini-3-pro-preview\agent_files_ft\circuit.stim",
        r"C:\Users\anpaz\Repos\quantum-ai\rq2\data\gemini-3-pro-preview\agent_files_ft\circuit_candidate.stim"
    )
