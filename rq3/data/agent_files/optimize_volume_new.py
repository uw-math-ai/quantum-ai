
import stim

def optimize_volume():
    with open("candidate_cleaned.stim", "r") as f:
        content = f.read()
    
    circuit = stim.Circuit(content)
    
    # Check if there are any CZs. If not, maybe we just have single qubit gates?
    # The circuit should have CZs.
    
    # Identify the cut point.
    # We assume:
    # 1. H layer (maybe empty)
    # 2. CZ layer
    # 3. Local corrections
    
    # We'll split the circuit into two parts: Before last CZ, and After last CZ.
    # The "After last CZ" part is what we optimize.
    
    last_cz_idx = -1
    for i, op in enumerate(circuit):
        if op.name == "CZ":
            last_cz_idx = i
            
    if last_cz_idx == -1:
        # No CZs? That's weird but possible (unentangled state).
        # Optimization is trivial then.
        before_cz = stim.Circuit()
        after_cz = circuit
    else:
        # Split
        before_cz = circuit[:last_cz_idx+1]
        after_cz = circuit[last_cz_idx+1:]
        
    # Process after_cz
    # For each qubit, compute the total Clifford
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
                t_op = stim.Tableau.from_name(gate_name)
                qubit_tableaus[q] = qubit_tableaus[q].then(t_op)
            else:
                # Handle measurement or reset? But prompt forbids introducing them.
                # If they exist, we can't easily merge.
                print(f"Error: Non-qubit target in post-processing: {t}")
                return

    # Synthesize minimal gates for each qubit
    qubit_gates = []
    for q in range(119):
        # synthesize output gates for this qubit
        t = qubit_tableaus[q]
        # t.to_circuit() returns a circuit that implements t
        # It's usually minimal-ish (H, S, H S, etc).
        c = t.to_circuit(method="elimination") 
        ops = [op.name for op in c]
        qubit_gates.append(ops)
        
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
            new_tail.append(gate, qubits)
            
    final_circuit = before_cz + new_tail
    
    with open("candidate_optimized.stim", "w") as f:
        f.write(str(final_circuit))
        
    print("Optimization complete.")

if __name__ == "__main__":
    optimize_volume()
