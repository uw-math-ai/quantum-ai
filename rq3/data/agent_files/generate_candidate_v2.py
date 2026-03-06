import stim

def convert_cz_to_cx(circuit):
    new_circuit = stim.Circuit()
    for instr in circuit:
        if instr.name == "CZ":
            targets = instr.targets_copy()
            for i in range(0, len(targets), 2):
                a = targets[i]
                b = targets[i+1]
                # CZ(a,b) = H(b) CX(a,b) H(b)
                new_circuit.append("H", [b])
                new_circuit.append("CX", [a, b])
                new_circuit.append("H", [b])
        else:
            new_circuit.append(instr)
    return new_circuit

def main():
    with open("current_task_stabilizers.txt", "r") as f:
        lines = [l.strip() for l in f if l.strip()]
    stabilizers = [stim.PauliString(l) for l in lines]
    
    print(f"Loaded {len(stabilizers)} stabilizers.")
    
    # Remove index 28 (the one that conflicts with 77)
    # We choose to remove 28 because baseline preserves 77.
    del stabilizers[28]
    print(f"Removed index 28. Count is now {len(stabilizers)}.")
    
    tableau = stim.Tableau.from_stabilizers(stabilizers, allow_underconstrained=True)
    graph_circuit = tableau.to_circuit(method="graph_state")
    
    # Convert CZ to CX
    cx_circuit = convert_cz_to_cx(graph_circuit)
    
    # Verify
    print(f"Candidate CX count: {cx_circuit.num_2_qubit_gates()}")
    
    with open("candidate_v2.stim", "w") as f:
        f.write(str(cx_circuit))

if __name__ == "__main__":
    main()
