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
        # allow_underconstrained is essential if n_stabilizers < n_qubits
        tableau = stim.Tableau.from_stabilizers(stabilizers, allow_underconstrained=True)
        
        # Synthesize using graph state method
        # This produces a circuit with H, S, CZ, etc.
        # CZ gates have 0 CX cost in Stim's default counting if we use them directly.
        circuit = tableau.to_circuit(method="graph_state")

        # Post-process to remove resets if we assume |0> start
        new_circuit = stim.Circuit()
        for instr in circuit:
            if instr.name == "RX":
                # RX resets to |+>. 
                # Since we start at |0>, we can replace RX with H.
                new_circuit.append("H", instr.targets_copy())
            elif instr.name == "R" or instr.name == "RX":
                 # Redundant if we assume initialized state
                 pass 
            elif instr.name == "TICK":
                 pass
            else:
                new_circuit.append(instr)
        
        # Print the circuit to stdout
        print(new_circuit)

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    generate_circuit()
