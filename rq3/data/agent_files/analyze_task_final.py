import stim
import sys

def load_stabilizers(filename):
    with open(filename, 'r') as f:
        lines = [line.strip() for line in f if line.strip()]
    return lines

def analyze_circuit(circuit_path, stabilizers_path):
    stabilizers = load_stabilizers(stabilizers_path)
    circuit = stim.Circuit.from_file(circuit_path)
    print(f"Loaded circuit with {len(circuit)} instructions.")
    
    # Metrics
    cx_count = 0
    volume = 0
    for op in circuit:
        if op.name == 'CX':
            cx_count += len(op.targets_copy()) // 2
        elif op.name == 'CZ':
            # Assuming CZ counts as a 2-qubit gate comparable to CX
            cx_count += len(op.targets_copy()) // 2
        
        # Volume: simplistic count of operations?
        # The prompt says "volume - total gate count in the volume gate set".
        # This usually means number of operations (unrolled).
        # But let's just count pairs for CX/CZ and 1 for others.
        if len(op.targets_copy()) > 1:
             volume += len(op.targets_copy()) # very rough
        else:
             volume += 1

    print(f"Baseline (recalc) 2Q-gate count: {cx_count}")
    print(f"Baseline (recalc) volume: {volume}")
    
    # Check stabilizers
    tableau = stim.TableauSimulator()
    tableau.do_circuit(circuit)
    
    preserved = 0
    total = len(stabilizers)
    
    for s_str in stabilizers:
        s = stim.PauliString(s_str)
        if tableau.peek_observable_expectation(s) == 1:
            preserved += 1
            
    print(f"Preserved {preserved}/{total} stabilizers.")

    # Try synthesis
    try:
        # Create a tableau from stabilizers
        parsed_stabilizers = [stim.PauliString(s) for s in stabilizers]
        
        # stim.Tableau.from_stabilizers returns a Tableau T.
        # The circuit for T prepares the state.
        
        t = stim.Tableau.from_stabilizers(parsed_stabilizers, allow_underconstrained=True, allow_redundant=True)
        synth_circuit = t.to_circuit("graph_state")
        
        synth_cx = 0
        synth_vol = 0
        for op in synth_circuit:
            if op.name in ['CX', 'CZ']:
                synth_cx += len(op.targets_copy()) // 2
            
            if len(op.targets_copy()) > 1:
                 synth_vol += len(op.targets_copy())
            else:
                 synth_vol += 1
        
        print(f"Synthesized circuit (graph_state) 2Q-gate count: {synth_cx}")
        print(f"Synthesized circuit (graph_state) volume: {synth_vol}")
        
        # Convert CZ to CX to check if it's better
        # This is a naive conversion, optimization might be needed.
        # But if the graph state is simple, it might be good enough.
        
        # We also want to save the synthesized circuit
        with open('synthesized_final.stim', 'w') as f:
            f.write(str(synth_circuit))
            
    except Exception as e:
        print(f"Synthesis failed: {e}")

if __name__ == "__main__":
    analyze_circuit("baseline_task_final.stim", "stabilizers_task_final.txt")
