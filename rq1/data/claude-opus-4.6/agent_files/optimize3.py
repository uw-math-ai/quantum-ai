import stim

# Current best circuit (volume=104)
# Let's see if we can optimize further by merging adjacent gate layers

# Try a cleaner version - merge same gate types
circuit_lines = []
circuit_lines.append("H 0 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 18 19")
circuit_lines.append("CZ 0 2 0 3 0 4 1 2 1 3 1 17 1 18 1 19 2 3 3 4 3 17 3 18 3 19 4 17 4 18 4 19 5 6 5 7 5 8 6 8 6 17 6 18 6 19 7 9 7 17 7 18 7 19 8 9 9 17 9 18 9 19 10 11 10 14 10 17 10 18 10 19 11 13 11 17 11 18 11 19 12 13 12 14 12 17 12 18 12 19 13 17 13 18 13 19 14 17 14 18 14 19 15 16 15 17 15 19 16 18 16 19 17 19 18 19")

# Apply single-qubit gates per qubit exactly matching the required transformation
# q0: Z
# q1: S SQRT_X_DAG
# q2: S SQRT_Y_DAG
# q3: S
# q4: (none)
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

# Apply gates qubit by qubit
for q in range(20):
    pass  # Build per-qubit

# Actually let's just try merging the layers better

# Merged version:
circuit_text = """H 0 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 18 19
CZ 0 2 0 3 0 4 1 2 1 3 1 17 1 18 1 19 2 3 3 4 3 17 3 18 3 19 4 17 4 18 4 19 5 6 5 7 5 8 6 8 6 17 6 18 6 19 7 9 7 17 7 18 7 19 8 9 9 17 9 18 9 19 10 11 10 14 10 17 10 18 10 19 11 13 11 17 11 18 11 19 12 13 12 14 12 17 12 18 12 19 13 17 13 18 13 19 14 17 14 18 14 19 15 16 15 17 15 19 16 18 16 19 17 19 18 19
Z 0
S 1 2 3 6 15
S_DAG 9 17
SQRT_X_DAG 5
X 7 8 11 14
Y 10 19
SQRT_Y_DAG 12 18
SQRT_Y 13
SQRT_X 16
SQRT_X_DAG 1
SQRT_Y_DAG 2
SQRT_Y 8
SQRT_X 9 10
S_DAG 11
S 14"""

circuit = stim.Circuit(circuit_text)

# Count gates
volume = 0
for inst in circuit:
    name = inst.name
    if name not in ["TICK", "DETECTOR", "OBSERVABLE_INCLUDE"]:
        if name in ["CX", "CZ", "CY", "SWAP", "ISWAP"]:
            volume += len(inst.targets_copy()) // 2
        else:
            volume += len(inst.targets_copy())

print(f"Volume: {volume}")
print(f"Circuit:\n{circuit}")

with open("data/claude-opus-4.6/agent_files/candidate_opt3.stim", "w") as f:
    f.write(str(circuit))
