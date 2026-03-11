import stim

def generate_circuit():
    try:
        # Read stabilizers
        with open("my_targets.txt", "r") as f:
            lines = [l.strip() for l in f.readlines() if l.strip()]

        stabilizers = []
        for line in lines:
            stabilizers.append(stim.PauliString(line))

        # Create tableau
        tableau = stim.Tableau.from_stabilizers(stabilizers, allow_underconstrained=True)
        
        # Synthesize using graph state method
        circuit = tableau.to_circuit(method="graph_state")

        # Post-process
        new_circuit = stim.Circuit()
        for instr in circuit:
            if instr.name == "RX":
                # Replace RX with H for |0> start
                new_circuit.append("H", instr.targets_copy())
            elif instr.name == "R":
                 # Remove R for |0> start
                 pass 
            elif instr.name == "TICK":
                 pass
            else:
                new_circuit.append(instr)
        
        # Write to file
        with open("candidate.stim", "w") as f:
            f.write(str(new_circuit))
            
        print("Candidate written to candidate.stim")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    generate_circuit()
