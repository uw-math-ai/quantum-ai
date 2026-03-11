import stim

def get_cx_count(circuit):
    cx_count = 0
    for instr in circuit:
        if instr.name in ["CX", "CNOT"]:
            cx_count += len(instr.targets_copy()) // 2
    return cx_count

def main():
    with open("current_baseline.stim", "r") as f:
        baseline_text = f.read()
    baseline = stim.Circuit(baseline_text)
    
    print(f"Baseline CX count: {get_cx_count(baseline)}")
    
    # Load stabilizers
    stabilizers = []
    with open("current_stabilizers.txt", "r") as f:
        for line in f:
            line = line.strip()
            if line:
                stabilizers.append(stim.PauliString(line))
    
    print(f"Loaded {len(stabilizers)} stabilizers.")
    
    # Try re-synthesis
    try:
        tableau = stim.Tableau.from_stabilizers(stabilizers, allow_underconstrained=True)
        circuit = tableau.to_circuit(method="graph_state")
        
        # Count CZ gates
        cz_count = 0
        for instr in circuit:
            if instr.name == "CZ":
                cz_count += len(instr.targets_copy()) // 2
        print(f"Graph state synthesis CZ count: {cz_count}")
        
        # Convert CZ to CX
        new_circuit = stim.Circuit()
        for instr in circuit:
            if instr.name == "CZ":
                targets = instr.targets_copy()
                for i in range(0, len(targets), 2):
                    t1 = targets[i]
                    t2 = targets[i+1]
                    new_circuit.append("H", [t2])
                    new_circuit.append("CX", [t1, t2])
                    new_circuit.append("H", [t2])
            else:
                new_circuit.append(instr)
        
        print(f"Converted circuit CX count: {get_cx_count(new_circuit)}")
        
        # Save candidate
        with open("candidate_graph.stim", "w") as f:
            f.write(str(new_circuit))
            
    except Exception as e:
        print(f"Synthesis failed: {e}")

if __name__ == "__main__":
    main()
