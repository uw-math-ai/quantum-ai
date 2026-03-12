import stim

def generate_graph_state_circuit(stabilizers_path):
    with open(stabilizers_path, 'r') as f:
        lines = [line.strip() for line in f if line.strip()]

    # Truncate unused trailing qubits
    max_len = max(len(l) for l in lines)
    padded_lines = [l.ljust(max_len, '_').replace('_', 'I') for l in lines]
    
    last_used_index = -1
    for i in range(max_len):
        if any(l[i] != 'I' for l in padded_lines):
            last_used_index = i
            
    truncated_lines = [l[:last_used_index+1] for l in padded_lines]
    
    # Create tableau from stabilizers
    # We allow underconstrained because we might have fewer stabilizers than qubits
    tableau = stim.Tableau.from_stabilizers([stim.PauliString(l) for l in truncated_lines], allow_underconstrained=True)

    # Synthesize circuit using graph_state method
    # This method naturally produces CZ gates and single qubit gates
    # It usually starts with resets (RX) if it assumes no input state, 
    # but we want to map this to a unitary starting from |0>.
    # RX is "reset to X basis i.e. |+>".
    # H on |0> -> |+>.
    # So replacing RX with H is the standard conversion for unitary synthesis from |0>.
    circuit = tableau.to_circuit(method="graph_state")
    
    new_circuit = stim.Circuit()
    for instruction in circuit:
        if instruction.name == "RX":
            # Replace RX with H
            targets = instruction.targets_copy()
            new_circuit.append("H", targets)
        elif instruction.name == "TICK":
            continue
        else:
            new_circuit.append(instruction)
            
    return new_circuit

if __name__ == "__main__":
    circuit = generate_graph_state_circuit("current_task_stabilizers.txt")
    with open("candidate.stim", "w") as f:
        print(circuit, file=f)
