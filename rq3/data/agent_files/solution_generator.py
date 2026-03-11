import stim

def solve():
    with open("target_stabilizers.txt", "r") as f:
        lines = [line.strip() for line in f if line.strip()]

    # Create tableau
    try:
        t = stim.Tableau.from_stabilizers([stim.PauliString(l) for l in lines], allow_underconstrained=True)
    except Exception as e:
        print(f"Error creating tableau: {e}")
        return

    # Synthesize
    circuit = t.to_circuit(method="graph_state")
    
    # Post-process to remove resets
    new_circuit = stim.Circuit()
    for instruction in circuit:
        if instruction.name == "RX":
            # RX resets to |+>. Since we start at |0>, H does the same.
            targets = instruction.targets_copy()
            new_circuit.append("H", targets)
        elif instruction.name == "RZ":
            # RZ resets to |0>. Since we start at |0>, this is Identity.
            pass
        else:
            new_circuit.append(instruction)

    # Write candidate
    with open("candidate.stim", "w") as f:
        f.write(str(new_circuit))

if __name__ == "__main__":
    solve()
