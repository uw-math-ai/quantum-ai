import stim

def main():
    try:
        with open('target_stabs_v3.txt', 'r') as f:
            content = f.read().strip()
            # Split by comma if present, otherwise lines
            if ',' in content:
                stabs = content.split(', ')
            else:
                stabs = content.split('\n')
        
        stabs = [s.strip() for s in stabs if s.strip()]
        paulis = [stim.PauliString(s) for s in stabs]
        
        # Generate graph state circuit
        # Using method='graph_state' typically gives 0 CX count (uses CZ)
        # allow_redundant=True is crucial as stabilizers might be linearly dependent
        # allow_underconstrained=True is crucial as we might have fewer stabilizers than qubits
        tableau = stim.Tableau.from_stabilizers(paulis, allow_redundant=True, allow_underconstrained=True)
        circuit = tableau.to_circuit(method='graph_state')
        
        # Replace RX with H. RX resets to |+>, H transforms |0> to |+>.
        # Since we want a unitary circuit from |0>, H is the correct equivalent.
        
        new_circuit = stim.Circuit()
        for instr in circuit:
            if instr.name == "RX":
                # Replace with H on same targets
                new_circuit.append("H", instr.targets_copy())
            else:
                new_circuit.append(instr)
                
        print(new_circuit)
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()
