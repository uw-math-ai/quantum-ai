import stim

def count_cx(circuit):
    count = 0
    for instr in circuit:
        if instr.name == "CX" or instr.name == "CNOT":
            if hasattr(instr, "targets_copy"):
                targets = instr.targets_copy()
            else:
                targets = instr.targets
            count += len(targets) // 2
    return count

def main():
    with open("baseline.stim", "r") as f:
        baseline_text = f.read()
    baseline = stim.Circuit(baseline_text)
    
    with open("stabilizers.txt", "r") as f:
        stabilizers = [line.strip() for line in f if line.strip()]

    # Check baseline preservation
    sim = stim.TableauSimulator()
    sim.do(baseline)
    preserved = 0
    for s_str in stabilizers:
        s = stim.PauliString(s_str)
        if sim.peek_observable_expectation(s) == 1:
            preserved += 1
            
    print(f"Baseline preserves {preserved}/{len(stabilizers)} stabilizers.")
    if preserved != len(stabilizers):
        print("Warning: Baseline does not preserve all stabilizers! Optimization might fail validity check.")

    # Try to resynthesize using tableau from circuit
    # Since from_stabilizers failed due to anticommutation, we use the circuit's tableau
    tableau = stim.Tableau.from_circuit(baseline)
    
    # Synthesize
    new_circuit = tableau.to_circuit("elimination")
    
    print(f"Baseline CX count: {count_cx(baseline)}")
    print(f"New Circuit CX count: {count_cx(new_circuit)}")
    
    with open("candidate.stim", "w") as f:
        f.write(str(new_circuit))

if __name__ == "__main__":
    main()
