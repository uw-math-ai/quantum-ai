import stim
import sys

def analyze_circuit(circuit):
    cx_count = 0
    volume = 0
    for instr in circuit:
        name = instr.name
        n_targets = len(instr.targets_copy())
        
        if name in ['CX', 'CNOT']:
            pairs = n_targets // 2
            cx_count += pairs
            volume += pairs
        elif name in ['CY', 'CZ', 'C_XYZ', 'C_ZYX']:
             pairs = n_targets // 2
             volume += pairs
        elif name in ['H', 'S', 'SQRT_X', 'X', 'Y', 'Z', 'I', 'S_DAG', 'SQRT_X_DAG', 'SQRT_Y', 'SQRT_Y_DAG', 'H_YZ', 'H_XY']:
             volume += n_targets
        elif name in ['RX', 'RY', 'RZ', 'R', 'M', 'MX', 'MY', 'MZ', 'MPP']:
             pass
    return cx_count, volume

def main():
    try:
        with open('current_baseline.stim', 'r') as f:
            baseline_text = f.read()
        baseline = stim.Circuit(baseline_text)
        b_cx, b_vol = analyze_circuit(baseline)
        print(f'Baseline: CX={b_cx}, Vol={b_vol}')
    except Exception as e:
        print(f'Error reading baseline: {e}')
        # return # Continue even if baseline fails, we need to generate candidate

    try:
        with open('current_target_stabilizers.txt', 'r') as f:
            lines = f.readlines()
        stabilizers = [line.strip() for line in lines if line.strip()]
        
        print(f'Loaded {len(stabilizers)} stabilizers.')
        
        # Create tableau
        tableau = stim.Tableau.from_stabilizers([stim.PauliString(s) for s in stabilizers])
        print(f'Tableau created. Qubits: {len(tableau)}')
        
        # Method 1: Graph State
        print('Attempting graph state synthesis...')
        circ_graph = tableau.to_circuit(method='graph_state')
        
        # Clean up RX gates (replace with H)
        circ_graph_clean = stim.Circuit()
        for instr in circ_graph:
            if instr.name == 'RX':
                # RX resets to |+>. Start state is |0>. H on |0> gives |+>.
                circ_graph_clean.append('H', instr.targets_copy())
            elif instr.name == 'R':
                # Reset to |0>. Start state is |0>. Identity.
                pass
            elif instr.name in ['M', 'MX', 'MY', 'MZ']:
                 pass
            else:
                 circ_graph_clean.append(instr)
        
        g_cx, g_vol = analyze_circuit(circ_graph_clean)
        print(f'Graph State (Cleaned): CX={g_cx}, Vol={g_vol}')
        
        with open('candidate_graph.stim', 'w') as f:
            f.write(str(circ_graph_clean))

    except Exception as e:
        print(f'Error in synthesis: {e}')

if __name__ == '__main__':
    main()
