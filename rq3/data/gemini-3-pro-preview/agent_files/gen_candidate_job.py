import stim

def main():
    # Read stabilizers
    with open('target_stabilizers_job.txt', 'r') as f:
        stabs = f.read().strip().split(', ')
    
    # Clean stabilizers (remove empty lines etc)
    stabs = [s.strip() for s in stabs if s.strip()]
    
    # Create PauliStrings
    paulis = [stim.PauliString(s) for s in stabs]
    
    # Create Tableau from stabilizers
    # allow_redundant=True because stabilizers might be dependent
    # allow_underconstrained=True because we might have fewer stabilizers than qubits
    tableau = stim.Tableau.from_stabilizers(paulis, allow_redundant=True, allow_underconstrained=True)
    
    # Synthesize circuit using graph state method (optimal for cx_count as it uses CZ)
    circuit = tableau.to_circuit(method='graph_state')
    
    # Post-process: graph_state method produces RX gates for initialization, but we want H gates for |0> -> |+>
    # Actually graph_state produces a circuit that prepares the state from |0>.
    # It usually looks like:
    # RX(0, 1, ...)  <-- This rotates Z basis |0> to Y basis? No, Stim's RX is X-rotation.
    # Wait, stim's graph_state returns a circuit that prepares the stabilizer state.
    # The documentation/memories say: "Stim's graph_state synthesis (via Tableau.from_stabilizers(...).to_circuit(method='graph_state')) produces circuits with 0 CX gates (using CZ instead) which are highly optimal for cx_count metrics. Remember to replace RX with H if starting from |0>."
    
    # Let's inspect the circuit.
    # If it uses RX, it might be doing rotations.
    # Usually graph state preparation is: H on all qubits, then CZ between neighbors, then local cliffords.
    
    print(circuit)

if __name__ == '__main__':
    main()
