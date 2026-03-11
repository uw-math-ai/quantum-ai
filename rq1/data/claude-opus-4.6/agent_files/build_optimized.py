import stim

# Build the optimized circuit with 42 CZ and optimized single-qubit gates
# Optimized sequences per qubit:
# q0: H SQRT_X_DAG
# q1: Y
# q2: S SQRT_X_DAG
# q3: H
# q4: SQRT_X
# q5: X S
# q6: SQRT_Y_DAG
# q7: SQRT_Y
# q8: S_DAG SQRT_X
# q9: S_DAG SQRT_Y_DAG
# q10: X
# q11: S_DAG
# q12: H SQRT_X_DAG
# q13: S
# q14: Z
# q15: H S
# q16: H
# q17: SQRT_X_DAG
# q18: SQRT_X_DAG

circuit_lines = []
circuit_lines.append("H 0 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 18 19")
circuit_lines.append("CZ 0 1 0 2 0 15 0 18 0 19 1 2 1 4 2 3 3 4 3 15 3 18 3 19 4 15 4 18 4 19 5 6 5 7 5 8 6 7 6 9 7 11 7 12 7 13 8 9 8 11 8 12 8 13 9 11 9 12 9 13 10 12 10 13 10 14 11 13 11 14 12 14 15 17 15 19 16 17 16 18 16 19 17 18")

# First layer single-qubit gates (first gate of each sequence)
circuit_lines.append("H 0 3 12 15 16")  # q0,3,12,15,16: first gate is H
circuit_lines.append("Y 1")  # q1: Y (done)
circuit_lines.append("S 2 13")  # q2,13: first gate is S (q13 done)
circuit_lines.append("SQRT_X 4")  # q4: SQRT_X (done)
circuit_lines.append("X 5 10")  # q5,10: first gate is X (q10 done)
circuit_lines.append("SQRT_Y_DAG 6")  # q6: SQRT_Y_DAG (done)
circuit_lines.append("SQRT_Y 7")  # q7: SQRT_Y (done)
circuit_lines.append("S_DAG 8 9 11")  # q8,9,11: first gate is S_DAG (q11 done)
circuit_lines.append("Z 14")  # q14: Z (done)
circuit_lines.append("SQRT_X_DAG 17 18")  # q17,18: SQRT_X_DAG (done)

# Second layer (second gate where applicable)
circuit_lines.append("SQRT_X_DAG 0 2 12")  # q0,2,12: second gate
circuit_lines.append("S 5 15")  # q5,15: second gate (q5 done, q15 done)
circuit_lines.append("SQRT_X 8")  # q8: second gate (q8 done)
circuit_lines.append("SQRT_Y_DAG 9")  # q9: second gate (q9 done)

optimized_circuit = "\n".join(circuit_lines)
print(optimized_circuit)

circuit = stim.Circuit(optimized_circuit)

# Count volume
volume = 0
for inst in circuit:
    name = inst.name
    if name not in ["TICK", "DETECTOR", "OBSERVABLE_INCLUDE"]:
        if name in ["CX", "CZ", "CY", "SWAP", "ISWAP"]:
            volume += len(inst.targets_copy()) // 2
        else:
            volume += len(inst.targets_copy())

print(f"\nVolume: {volume}")

with open("data/claude-opus-4.6/agent_files/candidate_final.stim", "w") as f:
    f.write(optimized_circuit)
