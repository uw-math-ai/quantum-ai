import stim

def count_gates(circuit):
    cx = 0
    cz = 0
    other = 0
    qubits = set()
    for instruction in circuit:
        for t in instruction.targets_copy():
            if t.is_qubit_target:
                qubits.add(t.value)
        if instruction.name == "CX" or instruction.name == "CNOT":
            cx += len(instruction.targets_copy()) // 2
        elif instruction.name == "CZ":
            cz += len(instruction.targets_copy()) // 2
        else:
            other += 1
    return cx, cz, other, len(qubits), max(qubits) if qubits else 0

try:
    with open("candidate_graph.stim", "r") as f:
        c = stim.Circuit(f.read())
        cx, cz, other, n_q, max_q = count_gates(c)
        print(f"Graph State Circuit:")
        print(f"CX: {cx}")
        print(f"CZ: {cz}")
        print(f"Other: {other}")
        print(f"Num qubits used: {n_q}")
        print(f"Max qubit index: {max_q}")
except Exception as e:
    print(f"Error reading candidate_graph.stim: {e}")

try:
    with open("candidate_elimination.stim", "r") as f:
        c = stim.Circuit(f.read())
        cx, cz, other, n_q, max_q = count_gates(c)
        print(f"\nElimination Circuit:")
        print(f"CX: {cx}")
        print(f"CZ: {cz}")
        print(f"Other: {other}")
except Exception as e:
    print(f"Error reading candidate_elimination.stim: {e}")
