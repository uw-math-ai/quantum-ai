import stim

def diagnose():
    with open("target_stabilizers.txt", "r") as f:
        lines = [line.strip() for line in f if line.strip()]

    print(f"Number of lines: {len(lines)}")
    lengths = [len(line) for line in lines]
    print(f"Min length: {min(lengths)}, Max length: {max(lengths)}")
    print(f"First line: {lines[0]}")
    print(f"Last line: {lines[-1]}")

    stabilizers = [stim.PauliString(line) for line in lines]
    print(f"First stabilizer len: {len(stabilizers[0])}")
    print(f"Last stabilizer len: {len(stabilizers[-1])}")

    try:
        t = stim.Tableau.from_stabilizers(stabilizers, allow_underconstrained=True)
        print(f"Tableau len: {len(t)}")
        
        circuit = t.to_circuit(method="graph_state")
        print("Generated circuit stats:")
        print(f"Num instructions: {len(circuit)}")
        # Check max qubit index in circuit
        max_q = -1
        for instr in circuit:
            for t in instr.targets_copy():
                if t.is_qubit_target:
                    max_q = max(max_q, t.value)
        print(f"Max qubit index in circuit: {max_q}")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    diagnose()
