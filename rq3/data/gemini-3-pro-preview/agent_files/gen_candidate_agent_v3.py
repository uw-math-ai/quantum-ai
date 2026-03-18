import stim

def main():
    try:
        # Load stabilizers
        with open('target_stabilizers_agent.txt', 'r') as f:
            stabilizers = [line.strip() for line in f if line.strip()]
        
        # Convert to Tableau
        # Note: stim.Tableau.from_stabilizers expects a list of stim.PauliString
        pauli_strings = [stim.PauliString(s) for s in stabilizers]
        
        # Synthesize circuit using graph state method
        # This typically yields H + CZ + local Cliffords
        # We use allow_redundant=True and allow_underconstrained=True to be safe
        tableau = stim.Tableau.from_stabilizers(pauli_strings, allow_redundant=True, allow_underconstrained=True)
        circuit = tableau.to_circuit(method="graph_state")
        
        # Replace RX with H since we assume start from |0> and resets are not allowed if not in baseline
        # Stim's graph_state synthesis usually starts with RX to prepare |+>
        # We can inspect the operations.
        new_circuit = stim.Circuit()
        for op in circuit:
            if op.name == "RX":
                # Replace RX with H
                new_circuit.append("H", op.targets_copy())
            else:
                new_circuit.append(op)
        
        # Save to file
        with open('candidate_1.stim', 'w') as f:
            f.write(str(new_circuit))
            
        print("Generated candidate_1.stim")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
