import stim

def generate_circuit():
    try:
        with open("target_stabilizers_job_v7.txt", "r") as f:
            lines = [line.strip().replace(",", "") for line in f if line.strip()]
        
        # Determine number of qubits from the first line
        if not lines:
            print("Error: No stabilizers found")
            return
            
        num_qubits = len(lines[0])
        
        # Convert strings to PauliStrings
        stabilizers = [stim.PauliString(line) for line in lines]
        
        # Create Tableau from stabilizers
        # allow_redundant=True because there might be redundant generators
        # allow_underconstrained=True because we might not specify full state
        try:
            tableau = stim.Tableau.from_stabilizers(stabilizers, allow_redundant=True, allow_underconstrained=True)
        except Exception as e:
            # Fallback: if from_stabilizers fails, maybe we need to be more specific or it's overconstrained
            print(f"Error creating tableau: {e}")
            return

        # Synthesize circuit
        circuit = tableau.to_circuit(method="graph_state")
        
        # Post-process circuit
        # 1. Remove initial resets (R)
        # 2. Replace RX with H if needed (graph_state might use H+CZ)
        
        new_circuit = stim.Circuit()
        for instruction in circuit:
            if instruction.name == "R" or instruction.name == "RX" or instruction.name == "RY" or instruction.name == "RZ":
                continue # Skip resets
            new_circuit.append(instruction)
            
        print(new_circuit)
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    generate_circuit()
