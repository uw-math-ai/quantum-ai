import stim
import sys

def load_stabilizers(filename):
    with open(filename, 'r') as f:
        lines = [l.strip() for l in f if l.strip()]
    return lines

def analyze_and_solve(stabilizer_file, baseline_file, output_file):
    print(f"Loading stabilizers from {stabilizer_file}...")
    stabilizers = load_stabilizers(stabilizer_file)
    num_qubits = len(stabilizers[0])
    print(f"Number of qubits: {num_qubits}")
    print(f"Number of stabilizers: {len(stabilizers)}")

    # Load baseline to check metrics
    print(f"Loading baseline from {baseline_file}...")
    with open(baseline_file, 'r') as f:
        baseline_text = f.read()
    baseline_circuit = stim.Circuit(baseline_text)
    # Count ops manually
    ops_counts = {}
    for op in baseline_circuit:
        ops_counts[op.name] = ops_counts.get(op.name, 0) + 1
    
    base_cx = ops_counts.get("CX", 0) + ops_counts.get("CNOT", 0)
    base_volume = sum(ops_counts.values())
    
    print(f"Baseline CX count: {base_cx}")
    print(f"Baseline Volume (approx): {base_volume}")

    # Method 1: Standard Gaussian Elimination
    print("Attempting synthesis with method='elimination'...")
    try:
        tableau = stim.Tableau.from_stabilizers([stim.PauliString(s) for s in stabilizers], allow_redundant=True, allow_underconstrained=True)
        circuit_elim = tableau.to_circuit(method="elimination")
        
        ops_elim = {}
        for op in circuit_elim:
            ops_elim[op.name] = ops_elim.get(op.name, 0) + 1
            
        cx_elim = ops_elim.get("CX", 0) + ops_elim.get("CNOT", 0)
        print(f"Elimination Circuit CX count: {cx_elim}")
        print(f"Elimination Circuit Volume: {sum(ops_elim.values())}")
    except Exception as e:
        print(f"Elimination method failed: {e}")
        circuit_elim = None

    # Method 2: Graph State Synthesis
    print("Attempting synthesis with method='graph_state'...")
    try:
        tableau = stim.Tableau.from_stabilizers([stim.PauliString(s) for s in stabilizers], allow_redundant=True, allow_underconstrained=True)
        circuit_graph = tableau.to_circuit(method="graph_state")
        
        ops_graph = {}
        for op in circuit_graph:
            ops_graph[op.name] = ops_graph.get(op.name, 0) + 1
            
        cz_count = ops_graph.get("CZ", 0)
        cx_graph = ops_graph.get("CX", 0) + ops_graph.get("CNOT", 0)
        print(f"Graph State Circuit CZ count: {cz_count}")
        print(f"Graph State Circuit CX count: {cx_graph}")
        print(f"Graph State Circuit Volume: {sum(ops_graph.values())}")
        
    except Exception as e:
        print(f"Graph State method failed: {e}")
        circuit_graph = None

    # Decide which circuit to use
    candidate = None
    # Prefer graph state if it has 0 CX (assuming CZ doesn't count as CX, which is typical for 'CX count' metric)
    # But wait, if CZ is allowed and CX count is the metric, then CZ based circuit has 0 CX.
    # If the metric includes CZ in volume but not CX count, then graph state is strictly better on CX count.
    
    if circuit_graph and cx_graph < base_cx:
        candidate = circuit_graph
        print("Selected Graph State circuit.")
    elif circuit_elim and cx_elim < base_cx:
        candidate = circuit_elim
        print("Selected Elimination circuit.")
    elif circuit_graph:
        candidate = circuit_graph
        print("Selected Graph State circuit (fallback).")
    elif circuit_elim:
        candidate = circuit_elim
        print("Selected Elimination circuit (fallback).")
    
    if candidate:
        print(f"Writing candidate to {output_file}...")
        with open(output_file, 'w') as f:
            f.write(str(candidate))
    else:
        print("No candidate generated.")

if __name__ == "__main__":
    analyze_and_solve("stabilizers_FINAL_REAL.txt", "baseline_FINAL_REAL.stim", "candidate.stim")
