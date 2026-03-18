import stim

# Original graph_state based circuit
circuit_str = """H 0 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 18 19 20 21 22 23 24 25 26 27 28 29 30 31 32 33 34 35 36 37 38 39 40 41 42 43 44 45 46 47 48
CZ 0 3 0 5 0 6 1 2 1 5 1 6 2 4 2 25 2 26 2 27 2 39 2 40 2 41 2 46 2 47 2 48 3 4 3 5 3 6 3 25 3 26 3 27 3 39 3 40 3 41 3 46 3 47 3 48 4 5 5 6 6 25 6 26 6 27 6 39 6 40 6 41 6 46 6 47 6 48 7 10 7 12 7 13 8 10 8 11 8 13 9 10 9 11 9 12 10 12 10 13 11 25 11 26 11 27 11 32 11 33 11 34 11 46 11 47 11 48 12 13 12 25 12 26 12 27 12 32 12 33 12 34 12 46 12 47 12 48 13 25 13 26 13 27 13 32 13 33 13 34 13 46 13 47 13 48 14 17 14 19 14 20 15 17 15 18 15 20 16 17 16 18 16 19 17 19 17 20 18 25 18 26 18 27 18 32 18 33 18 34 18 39 18 40 18 41 19 20 19 25 19 26 19 27 19 32 19 33 19 34 19 39 19 40 19 41 20 25 20 26 20 27 20 32 20 33 20 34 20 39 20 40 20 41 21 24 21 26 21 27 22 24 22 25 22 27 23 24 23 25 23 26 28 31 28 33 28 34 29 31 29 32 29 34 30 31 30 32 30 33 35 38 35 40 35 41 36 38 36 39 36 41 37 38 37 39 37 40 42 45 42 47 42 48 43 45 43 46 43 48 44 45 44 46 44 47
X 1 7 8 10 20 29 30 42
Y 11 12 15
Z 2 3 9 13 14 17 18 25 26 27 32 39 40 41 45 47 48
S 3 5 6 10 12 13 17 19 20
H 0 1 4 7 8 9 14 15 16 24 25 26 27 31 32 33 34 38 39 40 41 45 46 47 48
S 0 7 14"""

circuit = stim.Circuit(circuit_str)

# Simplified volume counting - count gate applications per qubit
def count_volume(circ):
    vol = 0
    cx_count = 0
    cz_count = 0
    for instr in circ:
        name = instr.name
        if name == 'TICK':
            continue
        targets = instr.targets_copy()
        if name in ['CX', 'CZ', 'CNOT']:
            # Two-qubit gates: each pair counts as 1
            num_pairs = len(targets) // 2
            if name == 'CX' or name == 'CNOT':
                cx_count += num_pairs
            else:
                cz_count += num_pairs
            vol += num_pairs
        else:
            # Single-qubit gates
            vol += len(targets)
    return vol, cx_count, cz_count

vol, cx, cz = count_volume(circuit)
print(f"Volume: {vol}, CX: {cx}, CZ: {cz}")

# Now try to simplify single-qubit gates
# Pauli X, Y, Z at end of circuit don't change stabilizer signs (only eigenvalues)
# But they do change stabilizer signs. For state prep they matter.

# Let's try removing TICK and minimizing
lines = circuit_str.strip().split('\n')
clean_lines = [line for line in lines if line.strip() and not line.strip().startswith('TICK')]
clean_circuit = stim.Circuit('\n'.join(clean_lines))

vol2, cx2, cz2 = count_volume(clean_circuit)
print(f"Without TICK - Volume: {vol2}, CX: {cx2}, CZ: {cz2}")

# Now let's try to find a more compact representation
# We can try to simplify single qubit gates

# Y = S_DAG * X * S = S * X * S_DAG (with global phase)
# More precisely: Y = i XZ, so Y|psi> ~ XZ|psi>
# For stabilizer circuits we can replace Y with X followed by Z or vice versa

# Try simplification: 
# 1. Convert Y to X + Z (Z first, then X = XZ = -iY)
# 2. Merge consecutive single qubit gates

def simplify_circuit(circ_str):
    lines = circ_str.strip().split('\n')
    result = []
    for line in lines:
        if line.strip().startswith('TICK'):
            continue
        if line.startswith('Y '):
            # Y = XZ (up to phase)
            qubits = line[2:]
            result.append('Z ' + qubits)
            result.append('X ' + qubits)
        else:
            result.append(line)
    return '\n'.join(result)

simplified = simplify_circuit(circuit_str)
simplified_circ = stim.Circuit(simplified)
print(f"\nSimplified circuit:")
print(simplified)

vol3, cx3, cz3 = count_volume(simplified_circ)
print(f"\nSimplified - Volume: {vol3}, CX: {cx3}, CZ: {cz3}")

# Save this circuit
with open('data/claude-opus-4.6/agent_files/candidate_v3.stim', 'w') as f:
    f.write(simplified)
