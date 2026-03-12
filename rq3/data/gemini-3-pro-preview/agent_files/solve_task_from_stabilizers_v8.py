import stim
import sys

def solve():
    print("Loading stabilizers...")
    with open('target_stabilizers_job.txt', 'r') as f:
        # Read entire content, remove newlines, split by comma
        content = f.read().replace('\n', '')
        parts = [s.strip() for s in content.split(',') if s.strip()]
    
    print(f"Loaded {len(parts)} stabilizer strings.")
    if not parts:
        print("No stabilizers found.")
        return

    # Convert to PauliString objects
    stabilizers = []
    for p_str in parts:
        try:
            stabilizers.append(stim.PauliString(p_str))
        except Exception as e:
            print(f"Error parsing stabilizer '{p_str}': {e}")
            return

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
                
        output_file = 'candidate_from_stabilizers_v8.stim'
        with open(output_file, 'w') as f:
            f.write(str(new_circuit))
        print(f"Done. Saved to {output_file}")

    except Exception as e:
        print(f"Failed to synthesize from stabilizers: {e}")

if __name__ == "__main__":
    solve()
