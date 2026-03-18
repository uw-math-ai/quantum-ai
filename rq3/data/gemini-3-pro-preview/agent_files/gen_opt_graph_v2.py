import stim
import sys

def solve():
    # 1. Read stabilizers
    stabilizers = []
    with open("target_stabilizers.txt", "r") as f:
        for line in f:
            line = line.strip()
            if line:
                stabilizers.append(line)

    # 2. Create Tableau
    try:
        t = stim.Tableau.from_stabilizers([stim.PauliString(s) for s in stabilizers], allow_redundant=True)
    except Exception as e:
        print(f"Error creating tableau: {e}")
        return

    # 3. Synthesize Circuit using graph_state method
    # This method produces circuits with only single-qubit gates and CZ gates.
    # CZ gates contribute 0 to cx_count (usually), effectively minimizing it.
    circuit = t.to_circuit(method="graph_state")

    # 4. Post-processing
    # The graph_state method might output RX gates (reset to X basis). 
    # Since we assume we start from |0>, RX is equivalent to H (creates |+>).
    # We also want to decompose any complex gates if necessary, but graph_state usually outputs simple gates.
    
    # We can iterate through instructions and replace RX with H.
    new_circuit = stim.Circuit()
    for instruction in circuit:
        if instruction.name == "RX":
            # RX target is reset to |+>. H on |0> is |+>.
            # We assume the circuit is state prep from |0>.
            for target in instruction.targets_copy():
                new_circuit.append("H", [target])
        else:
            new_circuit.append(instruction)

    # 5. Output the circuit
    with open("candidate.stim", "w") as f:
        f.write(str(new_circuit))

if __name__ == "__main__":
    solve()
