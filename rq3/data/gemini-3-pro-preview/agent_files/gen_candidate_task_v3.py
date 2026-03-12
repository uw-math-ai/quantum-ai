import stim
import sys

def main():
    stabilizers = []
    # Read from target_stabilizers.txt
    with open('target_stabilizers.txt', 'r') as f:
        for line in f:
            line = line.strip()
            if line:
                stabilizers.append(stim.PauliString(line))

    # Create Tableau from stabilizers
    # Use allow_underconstrained=True because 38 stabilizers < 42 qubits
    try:
        tableau = stim.Tableau.from_stabilizers(stabilizers, allow_underconstrained=True, allow_redundant=True)
    except Exception as e:
        print(f"Error creating tableau: {e}")
        sys.exit(1)

    # Synthesize circuit using graph_state method
    # This usually produces 0 CX gates (using CZ instead)
    circuit = tableau.to_circuit(method="graph_state")
    
    # Post-processing: Replace RX with H if input is |0>
    new_circuit = stim.Circuit()
    for instruction in circuit:
        if instruction.name == "RX":
            # Replace RX with H
            targets = instruction.targets_copy()
            new_circuit.append("H", targets)
        else:
            new_circuit.append(instruction)
            
    # Write to candidate_task.stim
    with open('candidate_task.stim', 'w') as f:
        f.write(str(new_circuit))
        
    print("Generated candidate_task.stim")

if __name__ == "__main__":
    main()
