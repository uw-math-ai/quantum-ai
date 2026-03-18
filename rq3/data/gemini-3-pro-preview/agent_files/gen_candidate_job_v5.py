import stim

def solve():
    # Read stabilizers
    with open('target_stabilizers_job_v5.txt', 'r') as f:
        stabs = [line.strip().replace(',', '') for line in f if line.strip()]
    
    # Create tableau
    try:
        # Convert strings to PauliStrings
        pauli_stabs = [stim.PauliString(s) for s in stabs]
        tableau = stim.Tableau.from_stabilizers(pauli_stabs, allow_redundant=True, allow_underconstrained=True)
    except Exception as e:
        print(f"Error creating tableau from stabilizers: {e}")
        # Fallback: extract from baseline
        print("Falling back to baseline tableau extraction")
        base = stim.Circuit.from_file('baseline_job_v5.stim')
        sim = stim.TableauSimulator()
        sim.do(base)
        tableau = sim.current_inverse_tableau().inverse()

    # Synthesize using graph state method
    # This naturally produces a circuit with 0 CX gates (using CZ instead)
    # which is the primary metric to optimize.
    circuit = tableau.to_circuit(method='graph_state')
    
    # Post-processing:
    # 1. Replace RX gates with H (since we start in |0>) if any
    # 2. Check if we need to clean up any initial/final gates
    
    clean_circuit = stim.Circuit()
    for instr in circuit:
        if instr.name == 'RX':
            # RX target is a reset X, which is equivalent to H * RZ * H * (measure Z) * (feedback)
            # But in the context of stabilizer states from |0>, usually just H is enough if it's preparation
            # However, 'method=graph_state' usually produces H on all qubits followed by CZs and local ops
            # If it produces RX, it might be a reset. 
            # Stim's graph state synthesis produces unitary circuits that prepare the state from |0>.
            # Let's inspect what it produces.
            clean_circuit.append('H', instr.targets_copy())
        else:
            clean_circuit.append(instr)
            
    # Remove any measurements or resets if they appeared (unlikely for graph_state method on tableau)
    # But graph_state synthesis might include resets if it thinks we are starting from scratch? 
    # Actually tableau.to_circuit(method='graph_state') returns a unitary circuit that maps |0> to the stabilizer state.
    
    print(clean_circuit)

if __name__ == "__main__":
    solve()
