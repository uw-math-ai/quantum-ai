import stim

# The circuit we have preserves all stabilizers. Let's try to optimize it further.

# Original circuit without TICK
circuit_str = """H 0 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 18 19 20 21 22 23 24 25 26 27 28 29 30 31 32 33 34 35 36 37 38 39 40 41 42 43 44 45 46 47 48
CZ 0 3 0 5 0 6 1 2 1 5 1 6 2 4 2 25 2 26 2 27 2 39 2 40 2 41 2 46 2 47 2 48 3 4 3 5 3 6 3 25 3 26 3 27 3 39 3 40 3 41 3 46 3 47 3 48 4 5 5 6 6 25 6 26 6 27 6 39 6 40 6 41 6 46 6 47 6 48 7 10 7 12 7 13 8 10 8 11 8 13 9 10 9 11 9 12 10 12 10 13 11 25 11 26 11 27 11 32 11 33 11 34 11 46 11 47 11 48 12 13 12 25 12 26 12 27 12 32 12 33 12 34 12 46 12 47 12 48 13 25 13 26 13 27 13 32 13 33 13 34 13 46 13 47 13 48 14 17 14 19 14 20 15 17 15 18 15 20 16 17 16 18 16 19 17 19 17 20 18 25 18 26 18 27 18 32 18 33 18 34 18 39 18 40 18 41 19 20 19 25 19 26 19 27 19 32 19 33 19 34 19 39 19 40 19 41 20 25 20 26 20 27 20 32 20 33 20 34 20 39 20 40 20 41 21 24 21 26 21 27 22 24 22 25 22 27 23 24 23 25 23 26 28 31 28 33 28 34 29 31 29 32 29 34 30 31 30 32 30 33 35 38 35 40 35 41 36 38 36 39 36 41 37 38 37 39 37 40 42 45 42 47 42 48 43 45 43 46 43 48 44 45 44 46 44 47
X 1 7 8 10 20 29 30 42
Y 11 12 15
Z 2 3 9 13 14 17 18 25 26 27 32 39 40 41 45 47 48
S 3 5 6 10 12 13 17 19 20
H 0 1 4 7 8 9 14 15 16 24 25 26 27 31 32 33 34 38 39 40 41 45 46 47 48
S 0 7 14"""

circuit = stim.Circuit(circuit_str)

# Try to simplify by tracking single-qubit gates per qubit
from collections import defaultdict

# Parse the circuit and track single-qubit operations
single_qubit_ops = defaultdict(list)
two_qubit_ops = []

for line in circuit_str.strip().split('\n'):
    parts = line.split()
    gate = parts[0]
    if gate in ['CZ', 'CX', 'CNOT']:
        qubits = list(map(int, parts[1:]))
        for i in range(0, len(qubits), 2):
            two_qubit_ops.append((gate, qubits[i], qubits[i+1]))
    else:
        qubits = list(map(int, parts[1:]))
        for q in qubits:
            single_qubit_ops[q].append(gate)

print("Single qubit operations per qubit:")
for q in sorted(single_qubit_ops.keys()):
    print(f"  Q{q}: {single_qubit_ops[q]}")

# Now try to simplify sequences of single-qubit gates
# H H = I
# S S = Z
# S S S S = I  
# X X = I
# Z Z = I
# H Z H = X
# H X H = Z
# S Z = Z S
# S X = Y S_DAG (up to phase) = -Y S_DAG (global phase)
# For stabilizer states, the global phase doesn't matter

def simplify_single_qubit_seq(ops):
    """Simplify a sequence of single-qubit Clifford gates."""
    # Convert to a more canonical form
    # Track the overall Clifford as a 2x2 matrix (mod 2) on (X, Z) 
    # and keep track of accumulated phases
    result = list(ops)
    
    # Basic simplifications
    changed = True
    while changed:
        changed = False
        new_result = []
        i = 0
        while i < len(result):
            if i + 1 < len(result):
                pair = (result[i], result[i+1])
                # HH = I
                if pair == ('H', 'H'):
                    i += 2
                    changed = True
                    continue
                # XX = I
                if pair == ('X', 'X'):
                    i += 2
                    changed = True
                    continue
                # ZZ = I
                if pair == ('Z', 'Z'):
                    i += 2
                    changed = True
                    continue
                # YY = I
                if pair == ('Y', 'Y'):
                    i += 2
                    changed = True
                    continue
                # SS = Z
                if pair == ('S', 'S'):
                    new_result.append('Z')
                    i += 2
                    changed = True
                    continue
            new_result.append(result[i])
            i += 1
        result = new_result
    
    return result

# Try simplifying
print("\nSimplified operations:")
simplified_ops = {}
for q in sorted(single_qubit_ops.keys()):
    simplified = simplify_single_qubit_seq(single_qubit_ops[q])
    simplified_ops[q] = simplified
    if simplified != single_qubit_ops[q]:
        print(f"  Q{q}: {single_qubit_ops[q]} -> {simplified}")

# Now construct the optimized circuit
# Structure: H on all qubits, CZ gates, then simplified single-qubit gates

# Check which qubits need H at the start
qubits_with_H = set()
for q, ops in single_qubit_ops.items():
    if 'H' in ops:
        qubits_with_H.add(q)

# All qubits that don't appear start with H from the initial H layer
all_qubits = set(range(49))
initial_H_qubits = all_qubits  # First line applies H to all

print(f"\nInitial H on all qubits: {sorted(initial_H_qubits)}")

# Build optimized circuit
# The structure is: H(all) -> CZ -> single-qubit corrections

# Let's use stim to verify we can simplify
# The simplest optimization is to remove redundant operations

# For now, let's output the best known circuit
best_circuit_str = circuit_str
print(f"\nBest circuit has {len(two_qubit_ops)} CZ gates")

# Save
with open('data/claude-opus-4.6/agent_files/best_v1.stim', 'w') as f:
    f.write(best_circuit_str)
