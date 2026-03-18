import stim

def check_qubits():
    with open("candidate_graph.stim", "r") as f:
        c = stim.Circuit(f.read())
    
    qubits_in_cz = set()
    for instruction in c:
        if instruction.name == "CZ":
            for t in instruction.targets_copy():
                qubits_in_cz.add(t.value)
    
    print(f"Qubits involved in CZ: {sorted(list(qubits_in_cz))}")
    print(f"Max qubit in CZ: {max(qubits_in_cz) if qubits_in_cz else 0}")

    with open("my_stabilizers.txt", "r") as f:
        lines = [l.strip() for l in f if l.strip()]
        if lines:
            print(f"First stabilizer length: {len(lines[0])}")
            print(f"Number of stabilizers: {len(lines)}")

if __name__ == "__main__":
    check_qubits()
