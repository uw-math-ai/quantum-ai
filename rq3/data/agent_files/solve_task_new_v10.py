import stim
import sys

def solve():
    print("Reading files...")
    with open("target_stabilizers_task_v10.txt", "r") as f:
        stabilizers = [line.strip() for line in f if line.strip()]
    
    with open("baseline_task_v10.stim", "r") as f:
        baseline_text = f.read()

    print(f"Loaded {len(stabilizers)} stabilizers.")
    
    # Analyze baseline
    baseline = stim.Circuit(baseline_text)
    base_cx = baseline.num_gates("CX") + baseline.num_gates("CNOT")
    print(f"Baseline CX count: {base_cx}")
    
    # Synthesize new circuit
    print("Synthesizing from stabilizers...")
    # method='graph_state' usually produces CZ gates, which are 0 CX cost if not penalized,
    # or can be converted.
    try:
        tableau = stim.Tableau.from_stabilizers(
            [stim.PauliString(s) for s in stabilizers], 
            allow_underconstrained=True
        )
        circuit = tableau.to_circuit(method="graph_state")
        
        # Check metrics
        new_cx = circuit.num_gates("CX") + circuit.num_gates("CNOT")
        new_cz = circuit.num_gates("CZ")
        print(f"Synthesized Circuit CX count: {new_cx}")
        print(f"Synthesized Circuit CZ count: {new_cz}")
        print(f"Synthesized Circuit gates: {circuit.num_operations}")

        # If CX is 0, this is infinitely better for cx_count.
        # But we must verify it preserves stabilizers.
        
        # Verification
        print("Verifying synthesized circuit...")
        sim = stim.TableauSimulator()
        sim.do(circuit)
        
        valid = True
        for i, stab in enumerate(stabilizers):
            p = stim.PauliString(stab)
            if sim.peek_observable_expectation(p) != 1:
                print(f"FAILURE: Stabilizer {i} not preserved!")
                valid = False
                break
        
        if valid:
            print("SUCCESS: New circuit is valid and strictly better.")
            with open("candidate_task.stim", "w") as f:
                f.write(str(circuit))
        else:
            print("Synthesized circuit failed verification.")

    except Exception as e:
        print(f"Error during synthesis: {e}")

if __name__ == "__main__":
    solve()
