import stim

# Try merging single-qubit gates
# Common simplifications:
# S S = Z
# Z H = H X
# X H = H Z (conjugate)
# Y = iXZ = S X S_DAG
# H S H = S_DAG (up to global phase)

# Let's build optimized sequences for each qubit
# The goal is to reduce single-qubit gate count

# Current sequences after CZ:
# q0: Z
# q1: Z H S -> H X S
# q2: Y S H -> 
# q3: S
# q5: S H S -> S_DAG H (or other 2-gate equiv)
# q6: S
# q7: X
# q8: Y H -> (need to compute)
# q9: Y H S -> (need to compute)
# q10: Z S H S -> (need to compute)
# q11: Y S -> (need to compute)
# q12: X H -> (need to compute)
# q13: Z H -> H X
# q14: X S -> (need to compute)
# q15: S
# q16: X S H S
# q17: Z S -> S_DAG (S S S = S_DAG, Z S = S_DAG)
# q18: X H -> SQRT_Y_DAG equivalent
# q19: Y

# Let's compute compositions using stim's tableau math
def gate_sequence_to_tableau(gates, n_qubits=1):
    """Apply gates to qubit 0 and return the tableau"""
    circ = stim.Circuit()
    for g in gates:
        circ.append(g, [0])
    return stim.Tableau.from_circuit(circ)

def find_equivalent_clifford(gates):
    """Find the equivalent Clifford for a sequence"""
    t = gate_sequence_to_tableau(gates)
    # Get how X and Z transform
    x_out = t.x_output(0)
    z_out = t.z_output(0)
    return str(x_out), str(z_out)

# Let me compute equivalents for each sequence
sequences = {
    0: ["Z"],
    1: ["Z", "H", "S"],
    2: ["Y", "S", "H"],
    3: ["S"],
    4: [],  # none
    5: ["S", "H", "S"],
    6: ["S"],
    7: ["X"],
    8: ["Y", "H"],
    9: ["Y", "H", "S"],
    10: ["Z", "S", "H", "S"],
    11: ["Y", "S"],
    12: ["X", "H"],
    13: ["Z", "H"],
    14: ["X", "S"],
    15: ["S"],
    16: ["X", "S", "H", "S"],
    17: ["Z", "S"],
    18: ["X", "H"],
    19: ["Y"],
}

print("Gate sequence transformations:")
for q, gates in sorted(sequences.items()):
    if gates:
        x_t, z_t = find_equivalent_clifford(gates)
        print(f"  Qubit {q}: {' '.join(gates)} -> X->{x_t}, Z->{z_t}")

# Let's find simpler representations
# Using tableau, generate all 1 and 2 gate Cliffords and match
single_gates = ["I", "X", "Y", "Z", "H", "S", "S_DAG", "SQRT_X", "SQRT_X_DAG", "SQRT_Y", "SQRT_Y_DAG"]

# Generate lookup table for 1-2 gate sequences
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
for q, gates in sorted(sequences.items()):
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

# Build optimized circuit
print("\n\nBuilding optimized circuit:")
circuit_lines = []
circuit_lines.append("H 0 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 18 19")
circuit_lines.append("CZ 0 2 0 3 0 4 1 2 1 3 1 17 1 18 1 19 2 3 3 4 3 17 3 18 3 19 4 17 4 18 4 19 5 6 5 7 5 8 6 8 6 17 6 18 6 19 7 9 7 17 7 18 7 19 8 9 9 17 9 18 9 19 10 11 10 14 10 17 10 18 10 19 11 13 11 17 11 18 11 19 12 13 12 14 12 17 12 18 12 19 13 17 13 18 13 19 14 17 14 18 14 19 15 16 15 17 15 19 16 18 16 19 17 19 18 19")

# Group optimized gates by type
gate_qubits = {}
for q, gates in sorted(optimized.items()):
    for gate in gates:
        if gate not in gate_qubits:
            gate_qubits[gate] = []
        gate_qubits[gate].append(str(q))

# Add gates in order
for gate in ["H", "S", "S_DAG", "X", "Y", "Z", "SQRT_X", "SQRT_X_DAG", "SQRT_Y", "SQRT_Y_DAG"]:
    if gate in gate_qubits:
        circuit_lines.append(f"{gate} {' '.join(gate_qubits[gate])}")

optimized_circuit = "\n".join(circuit_lines)
print(optimized_circuit)

# Verify
circuit = stim.Circuit(optimized_circuit)

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

print(f"\nOptimized: CX={cx_count}, CZ={cz_count}, Volume={volume}")

with open("data/claude-opus-4.6/agent_files/candidate_opt.stim", "w") as f:
    f.write(optimized_circuit)
