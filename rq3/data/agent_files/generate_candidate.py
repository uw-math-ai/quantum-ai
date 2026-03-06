import stim
import sys

def count_cx(circuit):
    count = 0
    for instr in circuit:
        if instr.name == 'CX' or instr.name == 'CNOT':
            count += len(instr.targets_copy()) // 2
    return count

def get_volume(circuit):
    count = 0
    for instr in circuit:
        if instr.name in ['CX', 'CY', 'CZ', 'H', 'S', 'SQRT_X', 'SQRT_Y', 'SQRT_Z', 'X', 'Y', 'Z', 'I', 'SWAP', 'ISWAP', 'SQRT_XX', 'SQRT_YY', 'SQRT_ZZ']:
             if instr.name in ['CX', 'CY', 'CZ', 'SWAP', 'ISWAP', 'SQRT_XX', 'SQRT_YY', 'SQRT_ZZ']:
                 count += len(instr.targets_copy()) // 2
             else:
                 count += len(instr.targets_copy())
    return count

def generate():
    with open('target_stabilizers.txt', 'r') as f:
        # Filter empty lines
        stabilizers = [line.strip().replace(',', '') for line in f if line.strip()]
        
    print(f'Loaded {len(stabilizers)} stabilizers.')
    
    # Method 1: Graph State Synthesis
    try:
        # We need PauliString objects
        paulis = [stim.PauliString(s) for s in stabilizers]
        tableau = stim.Tableau.from_stabilizers(paulis, allow_underconstrained=True)
        
        circuit_graph = tableau.to_circuit(method='graph_state')
        
        # Convert CZ to CX to get accurate CX count
        # CZ(a,b) = H(b) CX(a,b) H(b)
        circuit_cx = stim.Circuit()
        for instr in circuit_graph:
            if instr.name == 'CZ':
                targets = instr.targets_copy()
                for k in range(0, len(targets), 2):
                    p = targets[k].value
                    q = targets[k+1].value
                    circuit_cx.append('H', [q])
                    circuit_cx.append('CX', [p, q])
                    circuit_cx.append('H', [q])
            else:
                circuit_cx.append(instr)
                
        cx_graph = count_cx(circuit_cx)
        vol_graph = get_volume(circuit_cx)
        print(f'Method graph_state: CX={cx_graph}, Vol={vol_graph}')
        
        with open('candidate_graph.stim', 'w') as f:
            f.write(str(circuit_cx))
            
    except Exception as e:
        print(f'Method graph_state failed: {e}')

    # Method 2: Elimination Synthesis
    try:
        paulis = [stim.PauliString(s) for s in stabilizers]
        tableau = stim.Tableau.from_stabilizers(paulis, allow_underconstrained=True)
        
        circuit_elim = tableau.to_circuit(method='elimination')
        cx_elim = count_cx(circuit_elim)
        vol_elim = get_volume(circuit_elim)
        print(f'Method elimination: CX={cx_elim}, Vol={vol_elim}')
        
        with open('candidate_elimination.stim', 'w') as f:
            f.write(str(circuit_elim))

    except Exception as e:
        print(f'Method elimination failed: {e}')

if __name__ == '__main__':
    generate()
