import stim

with open(r'C:\Users\anpaz\Repos\quantum-ai\rq3\data\agent_files\candidate_optimized.stim', 'r') as f:
    circuit_text = f.read()

circuit = stim.Circuit(circuit_text)
cx = 0
cz = 0
others = 0

for instr in circuit:
    if instr.name == "CX" or instr.name == "CNOT":
        cx += len(instr.targets_copy()) // 2
    elif instr.name == "CZ":
        cz += len(instr.targets_copy()) // 2
    else:
        others += len(instr.targets_copy())

print(f"CX: {cx}")
print(f"CZ: {cz}")
print(f"Others: {others}")
