import stim

# Correctly apply the optimized gates in sequence per qubit
# The problem is that we need to apply all gates for each qubit in order

# Optimized sequences per qubit (from earlier analysis):
# q0: Z
# q1: S SQRT_X_DAG
# q2: S SQRT_Y_DAG
# q3: S
# q5: SQRT_X_DAG
# q6: S
# q7: X
# q8: X SQRT_Y
# q9: S_DAG SQRT_X
# q10: Y SQRT_X
# q11: X S_DAG
# q12: SQRT_Y_DAG
# q13: SQRT_Y
# q14: X S
# q15: S
# q16: SQRT_X
# q17: S_DAG
# q18: SQRT_Y_DAG
# q19: Y

# Build the circuit with gates in proper order
circuit_lines = []
circuit_lines.append("H 0 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 18 19")
circuit_lines.append("CZ 0 2 0 3 0 4 1 2 1 3 1 17 1 18 1 19 2 3 3 4 3 17 3 18 3 19 4 17 4 18 4 19 5 6 5 7 5 8 6 8 6 17 6 18 6 19 7 9 7 17 7 18 7 19 8 9 9 17 9 18 9 19 10 11 10 14 10 17 10 18 10 19 11 13 11 17 11 18 11 19 12 13 12 14 12 17 12 18 12 19 13 17 13 18 13 19 14 17 14 18 14 19 15 16 15 17 15 19 16 18 16 19 17 19 18 19")

# Now apply single-qubit gates per qubit in order
# Layer by layer approach - apply gates in specific order to maintain correctness

# First layer: first gate of each multi-gate sequence
circuit_lines.append("Z 0")  # q0: Z (done)
circuit_lines.append("S 1")  # q1: S (first of S SQRT_X_DAG)
circuit_lines.append("S 2")  # q2: S (first of S SQRT_Y_DAG)
circuit_lines.append("S 3 6 15")  # q3,6,15: S (done)
circuit_lines.append("SQRT_X_DAG 5")  # q5: SQRT_X_DAG (done)
circuit_lines.append("X 7 8 11 14")  # q7,8,11,14: X (first for 8,11,14)
circuit_lines.append("S_DAG 9 17")  # q9,17: S_DAG (first for q9, done for q17)
circuit_lines.append("Y 10 19")  # q10,19: Y (first for q10, done for q19)
circuit_lines.append("SQRT_Y_DAG 12 18")  # q12,18: SQRT_Y_DAG (done)
circuit_lines.append("SQRT_Y 13")  # q13: SQRT_Y (done)
circuit_lines.append("SQRT_X 16")  # q16: SQRT_X (done)

# Second layer: second gate of multi-gate sequences
circuit_lines.append("SQRT_X_DAG 1")  # q1: SQRT_X_DAG (second)
circuit_lines.append("SQRT_Y_DAG 2")  # q2: SQRT_Y_DAG (second)
circuit_lines.append("SQRT_Y 8")  # q8: SQRT_Y (second)
circuit_lines.append("SQRT_X 9 10")  # q9,10: SQRT_X (second)
circuit_lines.append("S_DAG 11")  # q11: S_DAG (second)
circuit_lines.append("S 14")  # q14: S (second)

optimized_circuit = "\n".join(circuit_lines)
print(optimized_circuit)

# Verify by parsing and checking
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

with open("data/claude-opus-4.6/agent_files/candidate_opt2.stim", "w") as f:
    f.write(optimized_circuit)
