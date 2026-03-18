
import stim
import sys

def solve():
    # Read stabilizers
    with open("current_task_stabilizers.txt", "r") as f:
        lines = [line.strip() for line in f if line.strip()]

    # Create tableau
    try:
        # stim.Tableau.from_stabilizers expects a list of stim.PauliString
        stabilizers = [stim.PauliString(line) for line in lines]
        tableau = stim.Tableau.from_stabilizers(stabilizers, allow_redundant=True, allow_underconstrained=True)
    except Exception as e:
        print(f"Error creating tableau: {e}")
        return

    # Synthesize circuit using graph_state method
    try:
        # The method returns a circuit that prepares the state.
        # "graph_state" is generally efficient for CZ/CX count.
        circuit = tableau.to_circuit(method="graph_state")
    except Exception as e:
        print(f"Error synthesizing circuit: {e}")
        return

    # Post-process to replace resets with unitary gates assuming |0> input
    new_circuit = stim.Circuit()
    for instruction in circuit:
        if instruction.name == "RX":
            # RX resets to |+>. From |0>, use H.
            for t in instruction.targets_copy():
                new_circuit.append("H", [t])
        elif instruction.name == "RY":
             # RY resets to |i+>. From |0>, use H then S.
             for t in instruction.targets_copy():
                 new_circuit.append("H", [t])
                 new_circuit.append("S", [t])
        elif instruction.name == "R" or instruction.name == "RZ":
             # R/RZ resets to |0>. From |0>, do nothing.
             pass
        else:
            new_circuit.append(instruction)

    # Write candidate
    with open("candidate.stim", "w") as f:
        f.write(str(new_circuit))

    print("Candidate generated.")

if __name__ == "__main__":
    solve()

