import stim

# Best circuit from ordering search (42 CZ)
circuit_text = """H 0 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 18 19
CZ 0 1 0 2 0 15 0 18 0 19 1 2 1 4 2 3 3 4 3 15 3 18 3 19 4 15 4 18 4 19 5 6 5 7 5 8 6 7 6 9 7 11 7 12 7 13 8 9 8 11 8 12 8 13 9 11 9 12 9 13 10 12 10 13 10 14 11 13 11 14 12 14 15 17 15 19 16 17 16 18 16 19 17 18
X 4 5 6 9 10
Y 1 8
Z 0 2 7 11 12 14
S 0 4 5 9 11 12 13 17 18
H 0 2 3 4 6 7 8 9 12 15 16 17 18
S 2 4 8 15 17 18"""

circuit = stim.Circuit(circuit_text)

# Count gates
cx_count = 0
cz_count = 0
volume = 0
for inst in circuit:
    name = inst.name
    if name == "CX":
        cx_count += len(inst.targets_copy()) // 2
    elif name == "CZ":
        cz_count += len(inst.targets_copy()) // 2
    if name not in ["TICK", "DETECTOR", "OBSERVABLE_INCLUDE"]:
        if name in ["CX", "CZ", "CY", "SWAP", "ISWAP"]:
            volume += len(inst.targets_copy()) // 2
        else:
            volume += len(inst.targets_copy())

print(f"Gate counts: CX={cx_count}, CZ={cz_count}, Volume={volume}")

# Analyze single-qubit gates per qubit
single_qubit_gates = {}
for i in range(20):
    single_qubit_gates[i] = []

# Parse the gates after CZ
gates_after_cz = """X 4 5 6 9 10
Y 1 8
Z 0 2 7 11 12 14
S 0 4 5 9 11 12 13 17 18
H 0 2 3 4 6 7 8 9 12 15 16 17 18
S 2 4 8 15 17 18"""

for line in gates_after_cz.strip().split('\n'):
    parts = line.split()
    gate = parts[0]
    qubits = [int(q) for q in parts[1:]]
    for q in qubits:
        single_qubit_gates[q].append(gate)

print("\nSingle-qubit gates per qubit after CZ:")
for q, gates in sorted(single_qubit_gates.items()):
    if gates:
        print(f"  Qubit {q}: {' '.join(gates)}")

# Optimize single-qubit sequences
def gate_sequence_to_tableau(gates):
    circ = stim.Circuit()
    for g in gates:
        circ.append(g, [0])
    return stim.Tableau.from_circuit(circ)

def find_equivalent_clifford(gates):
    t = gate_sequence_to_tableau(gates)
    x_out = t.x_output(0)
    z_out = t.z_output(0)
    return str(x_out), str(z_out)

# Build lookup table for 1-2 gate sequences
single_gates = ["I", "X", "Y", "Z", "H", "S", "S_DAG", "SQRT_X", "SQRT_X_DAG", "SQRT_Y", "SQRT_Y_DAG"]

clifford_lookup = {}
for g1 in single_gates:
    seq = [g1] if g1 != "I" else []
    x_t, z_t = find_equivalent_clifford(seq) if seq else ("+X", "+Z")
    clifford_lookup[(x_t, z_t)] = seq

for g1 in single_gates:
    for g2 in single_gates:
        if g1 == "I" or g2 == "I":
            continue
        seq = [g1, g2]
        x_t, z_t = find_equivalent_clifford(seq)
        if (x_t, z_t) not in clifford_lookup or len(clifford_lookup[(x_t, z_t)]) > 2:
            clifford_lookup[(x_t, z_t)] = seq

print("\nOptimized sequences:")
optimized = {}
for q, gates in sorted(single_qubit_gates.items()):
    if gates:
        x_t, z_t = find_equivalent_clifford(gates)
        if (x_t, z_t) in clifford_lookup:
            opt = clifford_lookup[(x_t, z_t)]
            optimized[q] = opt
            if len(opt) < len(gates):
                print(f"  Qubit {q}: {' '.join(gates)} ({len(gates)}) -> {' '.join(opt)} ({len(opt)})")
            else:
                print(f"  Qubit {q}: {' '.join(gates)} ({len(gates)}) = {' '.join(opt)} ({len(opt)})")
        else:
            optimized[q] = gates
            print(f"  Qubit {q}: {' '.join(gates)} (no shorter equivalent)")

# Calculate optimized volume
sq_gates_optimized = sum(len(gates) for gates in optimized.values())
total_volume_optimized = 20 + 42 + sq_gates_optimized  # H all + CZ + single-qubit
print(f"\nOptimized: H(20) + CZ(42) + SQ({sq_gates_optimized}) = {total_volume_optimized}")
