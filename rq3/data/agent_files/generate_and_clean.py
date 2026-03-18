import stim

def main():
    # Read stabilizers
    try:
        with open('target_stabilizers_v12.txt', 'r') as f:
            stabilizer_strs = [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        print("Error: target_stabilizers_v12.txt not found")
        return

    # Create tableau
    try:
        stabilizers = [stim.PauliString(s) for s in stabilizer_strs]
        tableau = stim.Tableau.from_stabilizers(stabilizers, allow_redundant=True, allow_underconstrained=True)
    except Exception as e:
        print(f"Error creating tableau: {e}")
        return

    # Synthesize circuit using elimination method
    circuit = tableau.to_circuit(method="elimination")

    # Post-process to remove resets if we assume start state |0>
    clean_circuit = stim.Circuit()
    for instruction in circuit:
        if instruction.name == "R" or instruction.name == "RZ":
            # Reset to 0. Since we start at 0, we can ignore this.
            pass
        elif instruction.name == "RX":
            # Reset to +. Since we start at 0, this is H.
            clean_circuit.append("H", instruction.targets_copy())
        elif instruction.name == "RY":
             # Reset to i. Since we start at 0, this is H then S.
             clean_circuit.append("H", instruction.targets_copy())
             clean_circuit.append("S", instruction.targets_copy())
        elif instruction.name == "TICK":
            pass
        else:
            clean_circuit.append(instruction)

    with open("candidate_elimination.stim", "w") as f:
        f.write(str(clean_circuit))
    
    print("Generated candidate_elimination.stim")

if __name__ == "__main__":
    main()
