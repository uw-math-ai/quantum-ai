import stim
import sys

def solve():
    print("Loading baseline...")
    with open("my_task_baseline.stim", "r") as f:
        baseline_text = f.read()
    baseline = stim.Circuit(baseline_text)
    
    print(f"Baseline gates: {len(baseline)}")
    print(f"Baseline num_qubits: {baseline.num_qubits}")

    # Count CX gates
    cx_count = sum(1 for op in baseline if op.name == "CX")
    print(f"Baseline CX count: {cx_count}")

    # Load stabilizers
    print("Loading stabilizers...")
    with open("my_target_stabilizers.txt", "r") as f:
        stabs_text = f.read().replace("\n", "").split(",")
    
    stabs_text = [s.strip() for s in stabs_text if s.strip()]
    print(f"Loaded {len(stabs_text)} stabilizers")
    print(f"Stabilizer length: {len(stabs_text[0])}")

    tableau_from_stabs = stim.Tableau.from_stabilizers([stim.PauliString(s) for s in stabs_text], allow_underconstrained=True)
    
    # Synthesize using graph state
    synth_circuit = tableau_from_stabs.to_circuit(method="graph_state")
    
    print("Synthesized circuit stats:")
    print(f"Gates: {len(synth_circuit)}")
    cx_count_synth = sum(1 for op in synth_circuit if op.name == "CX")
    cz_count_synth = sum(1 for op in synth_circuit if op.name == "CZ")
    print(f"CX count: {cx_count_synth}")
    print(f"CZ count: {cz_count_synth}")
    
    with open("my_candidate_graph.stim", "w") as f:
        f.write(str(synth_circuit))
        
if __name__ == "__main__":
    solve()
