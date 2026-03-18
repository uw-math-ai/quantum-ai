import stim

def synthesize_raw():
    with open("baseline_retry.stim", "r") as f:
        baseline = stim.Circuit(f.read())
    
    tableau = stim.Tableau.from_circuit(baseline)
    # Use graph_state method
    circuit = tableau.to_circuit(method="graph_state")
    
    with open("candidate_retry.stim", "w") as f:
        f.write(str(circuit))

if __name__ == "__main__":
    synthesize_raw()
