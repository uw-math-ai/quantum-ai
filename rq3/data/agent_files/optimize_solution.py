import stim

def solve():
    # Load stabilizers
    with open('target_stabilizers.txt', 'r') as f:
        stabilizers = [line.strip().replace(',', '') for line in f if line.strip()]
    
    # Check qubit count from length of first stabilizer
    num_qubits = len(stabilizers[0])
    print(f'Number of qubits from stabilizers: {num_qubits}')
    
    # Create Tableau
    try:
        print(f'Number of stabilizers: {len(stabilizers)}')
        
        tableau = stim.Tableau.from_stabilizers(stabilizers, allow_underconstrained=True)
        
        # Method 1: Graph state synthesis (uses CZ gates)
        circuit_graph = tableau.to_circuit(method='graph_state')
        
        # Check metrics for graph state circuit
        cx_count_graph = circuit_graph.num_gates('CX')
        print(f'Graph state circuit: {cx_count_graph} CX gates')
        
        # Write candidate
        with open('candidate.stim', 'w') as f:
            f.write(str(circuit_graph))
            
    except Exception as e:
        print(f'Error synthesizing: {e}')

    # Load baseline to compare
    with open('baseline.stim', 'r') as f:
        baseline_text = f.read()
    
    try:
        baseline = stim.Circuit(baseline_text)
        base_cx = baseline.num_gates('CX')
        print(f'Baseline CX count: {base_cx}')
    except Exception as e:
        print(f'Error reading baseline: {e}')

if __name__ == '__main__':
    solve()
