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
    cx_count = sum(1 for op in circuit if op.name == 'CX')
    # Approximate volume (all gates)
    volume = sum(1 for op in circuit)
    
    print(f"Baseline CX count: {cx_count}")
    print(f"Baseline volume: {volume}")
    
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
        
        t = stim.Tableau.from_stabilizers(parsed_stabilizers, allow_underconstrained=True)
        synth_circuit = t.to_circuit("graph_state")
        
        synth_cx = sum(1 for op in synth_circuit if op.name == 'CX')
        synth_cz = sum(1 for op in synth_circuit if op.name == 'CZ')
        synth_vol = sum(1 for op in synth_circuit)
        
        print(f"Synthesized circuit (graph_state) CX count: {synth_cx}")
        print(f"Synthesized circuit (graph_state) CZ count: {synth_cz}")
        print(f"Synthesized circuit (graph_state) volume: {synth_vol}")
        
        with open('synthesized.stim', 'w') as f:
            f.write(str(synth_circuit))
            
    except Exception as e:
        print(f"Synthesis failed: {e}")

if __name__ == "__main__":
    analyze_circuit("baseline_task_v9.stim", "stabilizers_task_v9.txt")
