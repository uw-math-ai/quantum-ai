import stim
import sys

def check_stabilizers():
    # Load target stabilizers
    with open(r'C:\Users\anpaz\Repos\quantum-ai\rq3\target_stabilizers_clean.txt', 'r') as f:
        target_stabilizers_str = [line.strip() for line in f if line.strip()]

    target_paulis = [stim.PauliString(s) for s in target_stabilizers_str]
    
    print(f"Loaded {len(target_paulis)} target stabilizers.")
    num_qubits = len(target_paulis[0])
    print(f"Number of qubits: {num_qubits}")

    # Load baseline circuit
    with open(r'C:\Users\anpaz\Repos\quantum-ai\rq3\baseline_prompt.stim', 'r') as f:
        baseline_circuit = stim.Circuit(f.read())
    
    print(f"Baseline circuit operations: {len(baseline_circuit)}")
    print(f"Baseline circuit qubits: {baseline_circuit.num_qubits}")

    # Simulate baseline to get its stabilizers
    sim = stim.TableauSimulator()
    sim.do(baseline_circuit)
    
    # Check if baseline satisfies targets
    preserved = 0
    for s in target_paulis:
        if sim.peek_observable_expectation(s) == 1:
            preserved += 1
    
    print(f"Baseline preserves {preserved}/{len(target_paulis)} target stabilizers.")
    
    if preserved != len(target_paulis):
        print("WARNING: Baseline does not preserve all target stabilizers!")
    
    # Check independence of target stabilizers
    try:
        # Create a tableau from stabilizers to check consistency and rank
        # We need to add dummy stabilizers if underconstrained to make it square for from_stabilizers?
        # Actually from_stabilizers takes a list and returns a Tableau if it defines a unique state.
        # If underconstrained, we can specify allow_underconstrained=True
        tableau = stim.Tableau.from_stabilizers(target_paulis, allow_underconstrained=True)
        print("Target stabilizers are consistent.")
        print(f"Tableau from stabilizers has {len(tableau)} qubits (size of support).")
        
        # We can try to synthesize a circuit from this tableau
        # If the tableau is valid, we can generate a circuit.
        
        # Optimization: Graph State
        try:
            # graph_state method works best if we start from a graph state tableau
            # But the tableau from stabilizers might not be in graph state form.
            # Convert to circuit
            circuit = tableau.to_circuit(method="graph_state")
            print("Successfully generated circuit using graph_state method.")
            print(f"Generated circuit metrics:")
            print(f"  CX count: {circuit.num_cx}")
            print(f"  Volume: {circuit.num_gates}") # Crude volume
            
            # Save this candidate
            with open(r'C:\Users\anpaz\Repos\quantum-ai\rq3\candidate_graph_state.stim', 'w') as f:
                f.write(str(circuit))
                
        except Exception as e:
            print(f"Failed to generate circuit from tableau: {e}")

    except Exception as e:
        print(f"Target stabilizers issue: {e}")

if __name__ == "__main__":
    check_stabilizers()
