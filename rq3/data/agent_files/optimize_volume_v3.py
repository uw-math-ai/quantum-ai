
import stim

def optimize_volume():
    with open("candidate_cleaned.stim", "r") as f:
        content = f.read()
    
    circuit = stim.Circuit(content)
    
    # Split into CZ part and single-qubit post-corrections
    last_cz_idx = -1
    for i, op in enumerate(circuit):
        if op.name == "CZ":
            last_cz_idx = i
            
    if last_cz_idx == -1:
        # No CZs? Just check the whole circuit
        before_cz = stim.Circuit()
        after_cz = circuit
    else:
        # Split
        before_cz = circuit[:last_cz_idx+1]
        after_cz = circuit[last_cz_idx+1:]
        
    # Process after_cz
    qubit_tableaus = [stim.Tableau(1) for _ in range(119)]
    
    for op in after_cz:
        gate_name = op.name
        targets = op.targets_copy()
        
        # Check if gate is single qubit
        if gate_name in ["CX", "CZ", "SWAP", "CNOT", "CY"]:
             print(f"Error: Found 2-qubit gate in post-processing block: {gate_name}")
             return

        for t in targets:
            if t.is_qubit_target:
                q = t.value
                t_op = stim.Tableau.from_circuit(stim.Circuit(f"{gate_name} 0"))
                qubit_tableaus[q] = qubit_tableaus[q].then(t_op)
            else:
                print(f"Error: Non-qubit target in post-processing: {t}")
                return

    # Synthesize minimal gates for each qubit
    qubit_gates = [[] for _ in range(119)]
    for q in range(119):
        t = qubit_tableaus[q]
        # Decompose into H, S, etc.
        # We can iterate through standard single qubit gates and find the shortest sequence that matches t.
        # But for now, let's just use to_circuit() which is decent.
        # Or better: brute force all 24 Cliffords.
        # Actually stim.Tableau.to_circuit("elimination") is good.
        c = t.to_circuit(method="elimination")
        for op in c:
             qubit_gates[q].append(op.name)
        
    # Schedule
    new_tail = stim.Circuit()
    max_len = max(len(g) for g in qubit_gates) if qubit_gates else 0
    
    for i in range(max_len):
        current_layer = {} 
        for q in range(119):
            if i < len(qubit_gates[q]):
                g = qubit_gates[q][i]
                if g not in current_layer:
                    current_layer[g] = []
                current_layer[g].append(q)
        
        for gate, qubits in current_layer.items():
            # If gate is I, skip
            if gate == "I": continue
            new_tail.append(gate, qubits)
            
    final_circuit = before_cz + new_tail
    
    with open("candidate_optimized.stim", "w") as f:
        f.write(str(final_circuit))
        
    print("Optimization complete.")

if __name__ == "__main__":
    optimize_volume()
