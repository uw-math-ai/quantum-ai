import stim

try:
    with open("target_stabilizers.txt") as f:
        lines = [line.strip() for line in f if line.strip()]

    # Parse stabilizers
    stabilizers = []
    for line in lines:
        stabilizers.append(stim.PauliString(line))
    
    print(f"Loaded {len(stabilizers)} stabilizers.")
    
    # Check if we have the right number of qubits
    num_qubits = len(stabilizers[0])
    print(f"Number of qubits: {num_qubits}")
    
    try:
        tableau = stim.Tableau.from_stabilizers(stabilizers)
        print("Successfully created tableau from stabilizers.")
        circuit = tableau.to_circuit()
        print("Generated circuit.")
        
        # Verify
        # We can use tableau to check if it stabilizes
        # But let's just output the circuit to a file
        with open("circuit_candidate.stim", "w") as f:
            f.write(str(circuit))
            
    except Exception as e:
        print(f"Error creating tableau: {e}")
        # If that fails, maybe the stabilizers are not independent or something.
        
except Exception as e:
    print(f"An error occurred: {e}")
