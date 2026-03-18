import stim
import sys

def optimize_solution():
    # Read stabilizers
    with open('target_stabilizers.txt', 'r') as f:
        stabilizers = [line.strip() for line in f if line.strip()]

    # Read baseline
    with open('baseline.stim', 'r') as f:
        baseline_text = f.read()
    baseline = stim.Circuit(baseline_text)

    # Try to synthesize from stabilizers using graph state
    try:
        print("Creating tableau...", file=sys.stderr)
        pauli_stabilizers = [stim.PauliString(s) for s in stabilizers]
        tableau = stim.Tableau.from_stabilizers(pauli_stabilizers, allow_redundant=True, allow_underconstrained=True)
        print(f"Tableau created. Qubits: {tableau.num_qubits}", file=sys.stderr)
        
        print("Converting to circuit...", file=sys.stderr)
        # Use graph state method which uses CZ gates instead of CX, often optimal for cx_count
        candidate = tableau.to_circuit(method='graph_state')
        print("Circuit created.", file=sys.stderr)
        
        # Replace RX with H (assuming start from |0>)
        new_circuit = stim.Circuit()
        for instr in candidate:
            if instr.name == 'RX':
                new_circuit.append('H', instr.targets_copy())
            else:
                new_circuit.append(instr.name, instr.targets_copy(), instr.gate_args_copy())
                
        print(new_circuit)
        
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return

if __name__ == '__main__':
    optimize_solution()
