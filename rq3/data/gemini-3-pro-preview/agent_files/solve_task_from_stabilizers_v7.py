import stim
import sys

def solve():
    print("Loading stabilizers...")
    with open('target_stabilizers_job.txt', 'r') as f:
        content = f.read()
        stabilizers = [s.strip() for s in content.split(',') if s.strip()]
    
    print(f"Loaded {len(stabilizers)} stabilizers.")
    if not stabilizers:
        print("No stabilizers found.")
        return

    # Determine number of qubits from length of first stabilizer
    num_qubits = len(stabilizers[0])
    print(f"Number of qubits: {num_qubits}")
    
    try:
        # Try to create tableau from stabilizers
        # allow_redundant=True is helpful if list is > n
        # allow_underconstrained=True is helpful if list is < n (fills with Z)
        tableau = stim.Tableau.from_stabilizers(stabilizers, allow_redundant=True, allow_underconstrained=True)
        print("Tableau created successfully.")
        
        print("Synthesizing graph state circuit...")
        circuit = tableau.to_circuit(method='graph_state')
        
        # Replace RX with H
        new_circuit = stim.Circuit()
        for instr in circuit:
            if instr.name == 'RX':
                new_circuit.append('H', instr.targets_copy())
            else:
                new_circuit.append(instr)
                
        with open('candidate_from_stabilizers.stim', 'w') as f:
            f.write(str(new_circuit))
        print("Done. Saved to candidate_from_stabilizers.stim")

    except Exception as e:
        print(f"Failed to synthesize from stabilizers: {e}")

if __name__ == "__main__":
    solve()
