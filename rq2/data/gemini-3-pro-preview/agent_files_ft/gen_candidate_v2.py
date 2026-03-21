import sys

def gen_candidate():
    # Read base circuit
    with open(r'data\gemini-3-pro-preview\agent_files_ft\circuit_v0.stim', 'r') as f:
        base_circuit = f.read().strip()
    
    # Read stabilizers
    with open(r'data\gemini-3-pro-preview\agent_files_ft\stabilizers.txt', 'r') as f:
        stabilizers = [line.strip() for line in f if line.strip()]
        
    ancilla_start = 85
    verification_ops = []
    flag_qubits = []
    
    current_ancilla = ancilla_start
    
    for stab in stabilizers:
        # Prepare ancilla in |+>
        verification_ops.append(f"H {current_ancilla}")
        
        # Apply controlled gates
        for q_idx, char in enumerate(stab):
            if char == 'X':
                verification_ops.append(f"CX {current_ancilla} {q_idx}")
            elif char == 'Z':
                verification_ops.append(f"CZ {current_ancilla} {q_idx}")
            elif char == 'Y':
                verification_ops.append(f"CY {current_ancilla} {q_idx}")
        
        # Measure in X basis (H + M)
        verification_ops.append(f"H {current_ancilla}")
        verification_ops.append(f"M {current_ancilla}")
        
        flag_qubits.append(current_ancilla)
        current_ancilla += 1
    
    full_circuit = base_circuit + "\n" + "\n".join(verification_ops)
    
    # Save to file for easy reading
    with open(r'data\gemini-3-pro-preview\agent_files_ft\candidate.stim', 'w') as f:
        f.write(full_circuit)
        
    # Print info for tool call
    print(f"Start Ancilla: {ancilla_start}")
    print(f"End Ancilla: {current_ancilla - 1}")
    print(f"Num Flags: {len(flag_qubits)}")
    
    # Print flag list for copy-paste
    print(f"FLAGS: {flag_qubits}")

if __name__ == "__main__":
    gen_candidate()
