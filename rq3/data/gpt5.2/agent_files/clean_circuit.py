import stim

# Read the candidate and convert RX to H
with open("agent_files/candidate1.stim", "r") as f:
    circuit_text = f.read()

# Replace RX with H (since starting from |0⟩, H|0⟩ gives |+⟩)
# Actually, RX resets to |+⟩ state. For a circuit starting from |0⟩, we need H to get |+⟩
# So RX q should be replaced with H q

lines = circuit_text.strip().split('\n')
new_lines = []
for line in lines:
    if line.startswith('RX '):
        # Replace RX with H
        qubits = line[3:]
        new_lines.append('H ' + qubits)
    else:
        new_lines.append(line)

# Also remove TICK lines if present
new_lines = [l for l in new_lines if l != 'TICK']

circuit_clean = '\n'.join(new_lines)
with open("agent_files/candidate1_clean.stim", "w") as f:
    f.write(circuit_clean)
print("Cleaned circuit saved")

# Check the circuit
c = stim.Circuit(circuit_clean)
cx, cz, h, s, vol = 0, 0, 0, 0, 0
for inst in c:
    nt = len(inst.targets_copy())
    if inst.name == 'CX': 
        cx += nt//2
        vol += nt//2
    elif inst.name == 'CZ': 
        cz += nt//2
        vol += nt//2
    elif inst.name == 'H': 
        h += nt
        vol += nt
    elif inst.name == 'S':
        s += nt
        vol += nt
    elif inst.name in ['X','Y','Z']:
        pass  # Paulis not counted in volume typically

print(f"CX={cx}, CZ={cz}, H={h}, S={s}, vol={vol}")
