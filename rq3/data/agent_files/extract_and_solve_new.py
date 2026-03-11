import stim

def solve():
    # Load baseline
    with open('current_task_baseline.stim', 'r') as f:
        baseline_text = f.read()
    
    circuit = stim.Circuit(baseline_text)
    
    # Extract stabilizers from baseline
    # We use TableauSimulator to get the canonical stabilizers of the output state
    # Actually, stim.Tableau.from_circuit(circuit) computes the unitary U.
    # The stabilizers of the state U|0> are given by U Z_i U^dag.
    # The 'z_output(k)' method of Tableau gives exactly these generators.
    # Wait, z_output(k) is U Z_k U^dag. Yes.
    
    tableau = stim.Tableau.from_circuit(circuit)
    stabilizers = []
    num_qubits = len(tableau)
    for k in range(num_qubits):
        stabilizers.append(tableau.z_output(k))
        
    # Synthesize new circuit from these stabilizers
    # Use graph_state for optimization
    try:
        # allow_redundant=True just in case
        new_tableau = stim.Tableau.from_stabilizers(stabilizers, allow_redundant=True, allow_underconstrained=True)
        # Use method='graph_state' for CZ based circuit (low CX count)
        new_circuit = new_tableau.to_circuit(method='graph_state')
        
        # Output the circuit
        with open('candidate_raw.stim', 'w') as f:
            f.write(str(new_circuit))
        print("Written to candidate_raw.stim")
        
    except Exception as e:
        print(f"Error synthesizing: {e}")

if __name__ == "__main__":
    solve()
