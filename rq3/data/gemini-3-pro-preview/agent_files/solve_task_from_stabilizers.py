import stim
import sys

def solve():
    stabilizers = []
    with open("current_target_stabilizers.txt", "r") as f:
        for line in f:
            line = line.strip()
            if line:
                stabilizers.append(stim.PauliString(line))

    # Create Tableau
    try:
        # allow_redundant=True because the list might be overcomplete
        tableau = stim.Tableau.from_stabilizers(stabilizers, allow_redundant=True)
    except Exception as e:
        print(f"Error creating tableau: {e}")
        return

    # Synthesize circuit using graph_state method (optimizes for CZ, 0 CX)
    circuit = tableau.to_circuit(method="graph_state")

    # Post-process circuit to replace RX with H if we assume input is |0>
    new_circuit = stim.Circuit()
    for instruction in circuit:
        if instruction.name == "RX":
            # RX resets to |+>. If input is |0>, H also prepares |+>.
            # If input is anything else, this logic is faulty, but standard tasks assume |0>.
            for target in instruction.targets_copy():
                new_circuit.append("H", [target])
        else:
            new_circuit.append(instruction)

    print(new_circuit)

if __name__ == "__main__":
    solve()
