import stim

with open('candidate_graph.stim', 'r') as f:
    lines = f.readlines()

new_lines = []
for line in lines:
    if line.strip().startswith('RX'):
        # Replace RX with H
        qubits = line.strip().split()[1:]
        new_lines.append(f"H {' '.join(qubits)}\n")
    elif line.strip() == "TICK":
        continue
    else:
        new_lines.append(line)

with open('candidate_clean.stim', 'w') as f:
    f.writelines(new_lines)

# Verify
circuit = stim.Circuit("".join(new_lines))
print(f"Cleaned circuit loaded. {circuit.num_qubits} qubits.")

# Count
cx = 0
cz = 0
volume = 0
for op in circuit:
    if op.name in ["CX", "CNOT"]:
        cx += len(op.targets_copy()) // 2
    elif op.name == "CZ":
        cz += len(op.targets_copy()) // 2
    
    # Volume calculation
    if op.name in ["QUBIT_COORDS", "SHIFT_COORDS", "DETECTOR", "OBSERVABLE_INCLUDE", "TICK"]:
        continue
    n_args = 1
    if op.name in ["CX", "CNOT", "CZ", "SWAP", "ISWAP", "CY", "XCZ", "XCY", "XCX"]:
        n_args = 2
    args = len(op.targets_copy())
    volume += args // n_args

print(f"CX count: {cx}")
print(f"CZ count: {cz}")
print(f"Volume: {volume}")
print(f"Total 2Q gates: {cx + cz}")

# Check stabilizers
with open('my_task_stabilizers.txt', 'r') as f:
    stabilizers = [l.strip() for l in f.readlines() if l.strip()]

sim = stim.TableauSimulator()
sim.do(circuit)
preserved = 0
for s_str in stabilizers:
    p = stim.PauliString(s_str)
    if sim.peek_observable_expectation(p) == 1:
        preserved += 1

print(f"Preserved: {preserved}/{len(stabilizers)}")

# If we convert CZ to CX+H+H
# Each CZ becomes 1 CX + 2 H.
# Volume increases by 2 * cz_count (for the H gates).
# CX count becomes cz_count.
projected_cx = cx + cz
projected_volume = volume + 2 * cz 
print(f"Projected metrics if CZ->CX: CX={projected_cx}, Vol={projected_volume}")
