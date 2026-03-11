import stim

def diagnose():
    # Check baseline
    with open("baseline.stim", "r") as f:
        baseline_text = f.read()
    baseline = stim.Circuit(baseline_text)
    print(f"Baseline num_qubits: {baseline.num_qubits}")
    
    # Check tableau
    tableau = baseline.to_tableau()
    print(f"Tableau num_qubits: {len(tableau)}")
    
    # Check candidate
    with open("candidate.stim", "r") as f:
        candidate_text = f.read()
    candidate = stim.Circuit(candidate_text)
    print(f"Candidate num_qubits: {candidate.num_qubits}")
    
    # Check stabilizers
    stabs = [
        "XXXXIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIII",
        "IIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIXXXXI"
    ]
    print(f"Stabilizer length: {len(stabs[0])}")

diagnose()
