import stim
import sys

def solve():
    # Read stabilizers
    with open('target_stabilizers_final.txt', 'r') as f:
        content = f.read().strip()
        # The content might be comma separated or newlines.
        # The prompt shows comma separated.
        if ',' in content:
            stabilizers = [s.strip() for s in content.split(',') if s.strip()]
        else:
            stabilizers = [s.strip() for s in content.split('\n') if s.strip()]

    # Validate stabilizers and get qubit count
    if not stabilizers:
        print("No stabilizers found")
        return

    n_qubits = len(stabilizers[0])
    print(f"Number of qubits: {n_qubits}")
    print(f"Number of stabilizers: {len(stabilizers)}")

    stabilizers_obj = [stim.PauliString(s) for s in stabilizers]
    
    # Synthesize circuit
    try:
        # Create a tableau from stabilizers
        # allow_underconstrained=True because we might not specify all degrees of freedom
        tableau = stim.Tableau.from_stabilizers(stabilizers_obj, allow_underconstrained=True, allow_redundant=True)
        
        # Synthesize using graph_state method which uses CZs and is optimal for cx_count (0 CXs)
        circuit = tableau.to_circuit(method='graph_state')
        
        # Post-processing:
        # The graph state synthesis might include 'RX' or 'R' gates for resetting.
        # But our baseline assumes initialized |0> state and uses H and CX.
        # 'RX' is equivalent to Reset to |0> then H.
        # If the circuit starts with RX on a qubit, it means "Reset this qubit to |0>, then apply H".
        # Since we assume the qubits start in |0>, 'RX' is just 'H'.
        # 'R' means "Reset to |0>". Since we start in |0>, 'R' is Identity (can be removed).
        
        new_circuit = stim.Circuit()
        for instr in circuit:
            if instr.name == 'RX':
                # Replace RX target with H target
                new_circuit.append('H', instr.targets_copy())
            elif instr.name == 'R':
                # Remove R gates as we assume initialization
                pass
            else:
                new_circuit.append(instr)
                
        # Also check for 'MX' or 'M' measurements which shouldn't be there for a state prep circuit
        # graph_state synthesis usually doesn't put measurements unless specified.
        
        # Output the circuit
        print("Synthesized circuit:")
        print(new_circuit)
        
        # Save to file
        with open('candidate.stim', 'w') as f:
            f.write(str(new_circuit))
            
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    solve()
