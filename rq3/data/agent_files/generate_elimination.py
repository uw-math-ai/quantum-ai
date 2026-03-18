import stim

def solve_elim():
    with open("baseline.stim", "r") as f:
        baseline_text = f.read()
    baseline = stim.Circuit(baseline_text)
    tableau = baseline.to_tableau()
    
    # Use elimination method
    candidate = tableau.to_circuit(method="elimination")
    
    # Save
    with open("candidate_elim.stim", "w") as f:
        f.write(str(candidate))
        
    print(f"Generated candidate_elim.stim. Num qubits: {candidate.num_qubits}")

solve_elim()
