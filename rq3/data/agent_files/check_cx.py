import stim

with open("final_candidate.stim", "r") as f:
    circuit = stim.Circuit(f.read())

cx = 0
vol = 0
for instr in circuit:
     if instr.name in ["CX", "CNOT", "CY", "CZ", "SWAP", "ISWAP", "CXSWAP", "SWAPCX", "SQRT_XX", "SQRT_YY", "SQRT_ZZ"]:
         n = len(instr.targets_copy())
         cx += n // 2
         vol += n // 2
     elif instr.name in ["H", "S", "S_DAG", "SQRT_X", "SQRT_X_DAG", "SQRT_Y", "SQRT_Y_DAG", "SQRT_Z", "SQRT_Z_DAG", "X", "Y", "Z", "I"]:
         n = len(instr.targets_copy())
         vol += n

print(f"Final CX: {cx}")
print(f"Final Volume: {vol}")

# Also compare to baseline
with open("baseline.stim", "r") as f:
    baseline = stim.Circuit(f.read())

b_cx = 0
b_vol = 0
for instr in baseline:
     if instr.name in ["CX", "CNOT", "CY", "CZ", "SWAP", "ISWAP", "CXSWAP", "SWAPCX", "SQRT_XX", "SQRT_YY", "SQRT_ZZ"]:
         n = len(instr.targets_copy())
         b_cx += n // 2
         b_vol += n // 2
     elif instr.name in ["H", "S", "S_DAG", "SQRT_X", "SQRT_X_DAG", "SQRT_Y", "SQRT_Y_DAG", "SQRT_Z", "SQRT_Z_DAG", "X", "Y", "Z", "I"]:
         n = len(instr.targets_copy())
         b_vol += n

print(f"Baseline CX: {b_cx}")
print(f"Baseline Volume: {b_vol}")

if cx < b_cx or (cx == b_cx and vol < b_vol):
    print("IMPROVEMENT CONFIRMED")
else:
    print("NO IMPROVEMENT")
