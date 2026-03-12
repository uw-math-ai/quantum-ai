import stim

def generate_candidate():
    # Load stabilizers
    with open('target_stabilizers_job_v6.txt', 'r') as f:
        content = f.read().replace('\n', ',').replace(' ', '')
        stabs = [s.strip() for s in content.split(',') if s.strip()]

    # Parse stabilizers
    # Note: stabs list contains strings like "XXXX..."
    # We need to convert them to stim.PauliString
    pauli_stabs = []
    for s in stabs:
        try:
            pauli_stabs.append(stim.PauliString(s))
        except Exception as e:
            print(f"Error parsing stabilizer: {s} -> {e}")

    print(f"Loaded {len(pauli_stabs)} stabilizers")
    
    # Synthesize circuit
    try:
        tableau = stim.Tableau.from_stabilizers(pauli_stabs, allow_redundant=True, allow_underconstrained=True)
        circuit = tableau.to_circuit(method="graph_state")
        
        # Optimize: Replace RX with H if possible?
        # Graph state synthesis usually uses H and CZ.
        # It initializes qubits in |0>, does H, then CZ, then maybe local Cliffords.
        # Check if any RX gates are generated (Stim sometimes uses RX to prepare |+>)
        # We can just output the circuit as is first.
        
        with open('candidate_job_v6.stim', 'w') as f:
            f.write(str(circuit))
            
        print("Candidate generated successfully.")
        
    except Exception as e:
        print(f"Error synthesizing: {e}")

if __name__ == "__main__":
    generate_candidate()
