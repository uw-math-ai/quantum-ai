import stim
import sys

def generate_candidate():
    try:
        with open("target_stabilizers_current.txt", "r") as f:
            lines = [line.strip() for line in f if line.strip()]
        
        # Convert to PauliStrings
        stabilizers = [stim.PauliString(line) for line in lines]
        
        # Create Tableau
        # Note: stim.Tableau.from_stabilizers returns a Tableau that represents the state.
        # It maps Z_k -> stabilizer_k.
        tableau = stim.Tableau.from_stabilizers(
            stabilizers,
            allow_redundant=True,
            allow_underconstrained=True
        )
        
        # Synthesize circuit using graph_state method
        circuit = tableau.to_circuit(method="graph_state")
        
        new_circuit = stim.Circuit()
        for instruction in circuit:
            if instruction.name == "RX":
                # RX resets to X basis. From |0>, H does that.
                for target in instruction.targets_copy():
                    new_circuit.append("H", [target])
            elif instruction.name == "R":
                 # R (Reset Z). From |0>, does nothing.
                 pass
            elif instruction.name == "M" or instruction.name == "MX" or instruction.name == "MY" or instruction.name == "MZ":
                 print(f"Warning: Measurement {instruction.name} encountered. Skipping.")
            else:
                new_circuit.append(instruction)
                
        # Save candidate
        with open("candidate_graph_state_v6.stim", "w") as f:
            f.write(str(new_circuit).replace("tick", "")) 

        print("Candidate generated: candidate_graph_state_v6.stim")
        
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    generate_candidate()
