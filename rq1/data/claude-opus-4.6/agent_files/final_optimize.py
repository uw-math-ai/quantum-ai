import stim

# Define stabilizers for 15 qubits
stabilizers = [
    "IIIIIIIXXXXXXXX",  # X on 7-14
    "IIIXXXXIIIIXXXX",  # X on 3-6, 11-14
    "IXXIIXXIIXXIIXX",  # X on 1-2, 5-6, 9-10, 13-14
    "XIXIXIXIXIXIXIX",  # X on 0, 2, 4, 6, 8, 10, 12, 14
    "IIIIIIIZZZZZZZZ",  # Z on 7-14
    "IIIZZZZIIIIZZZZ",  # Z on 3-6, 11-14
    "IZZIIZZIIZZIIZZ",  # Z on 1-2, 5-6, 9-10, 13-14
    "ZIZIZIZIZIZIZIZ",  # Z on 0, 2, 4, 6, 8, 10, 12, 14
]

def test_circuit(circuit_str, stabilizers):
    """Test if a circuit preserves all stabilizers."""
    test_circuit = stim.Circuit(circuit_str)
    sim = stim.TableauSimulator()
    sim.do_circuit(test_circuit)
    
    results = []
    for s in stabilizers:
        ps = stim.PauliString(s)
        exp = sim.peek_observable_expectation(ps)
        results.append(exp == 1)
    return all(results), results

def count_gates(circuit_str):
    """Count CX and H gates in a circuit."""
    circuit = stim.Circuit(circuit_str)
    cx_count = 0
    h_count = 0
    for inst in circuit:
        if inst.name == 'CX':
            cx_count += len(list(inst.targets_copy())) // 2
        elif inst.name == 'H':
            h_count += len(list(inst.targets_copy()))
    return cx_count, h_count

# Current best circuit (28 CX, 4 H)
best_circuit = """H 0
H 1
H 3
H 7
CX 0 2
CX 1 2
CX 0 4
CX 3 4
CX 1 5
CX 3 5
CX 0 6
CX 1 6
CX 3 6
CX 0 8
CX 7 8
CX 1 9
CX 7 9
CX 0 10
CX 1 10
CX 7 10
CX 3 11
CX 7 11
CX 0 12
CX 3 12
CX 7 12
CX 1 13
CX 3 13
CX 7 13
CX 0 14
CX 1 14
CX 3 14
CX 7 14"""

passes, results = test_circuit(best_circuit, stabilizers)
cx, h = count_gates(best_circuit)
print(f"Current best: CX={cx}, H={h}, passes={passes}")

# Try to use graph state approach with CZ instead of CX
# CZ is symmetric and might allow for fewer gates

# Graph state circuit from earlier (with H instead of RX):
graph_circuit = """H 0 1 2 3 4 5 6 7 8 9 10 11 12 13 14
CZ 0 1 0 2 1 4 1 5 1 8 1 9 1 12 1 13 2 4 2 6 2 8 2 10 2 12 2 14 3 4 3 5 3 6 3 11 3 12 3 13 3 14 4 5 4 6 4 11 4 12 4 13 4 14 5 6 5 11 5 12 5 13 5 14 6 11 6 12 6 13 6 14 7 8 7 9 7 10 7 11 7 12 7 13 7 14 11 12 11 13 11 14 12 13 12 14 13 14
X 2
Z 0 4 6 8 10 12 14
S 3 4 5 6 11 12 13 14
H 0 3 4 5 6 8 9 10 11 12 13 14
S 3"""

passes_graph, _ = test_circuit(graph_circuit, stabilizers)
print(f"Graph state circuit passes: {passes_graph}")

# Count CZ gates in graph circuit
graph_c = stim.Circuit(graph_circuit)
cz_count = 0
for inst in graph_c:
    if inst.name == 'CZ':
        cz_count += len(list(inst.targets_copy())) // 2
print(f"Graph state circuit: CZ={cz_count}")

# Try to optimize the CX circuit by reordering
# Each data qubit needs connections to specific check qubits:
# data  check_qubits_needed (based on binary of data+1)
# 2:    0, 1      (3 = 011)
# 4:    0, 3      (5 = 101)
# 5:    1, 3      (6 = 110)
# 6:    0, 1, 3   (7 = 111)
# 8:    0, 7      (9 = 1001)
# 9:    1, 7      (10 = 1010)
# 10:   0, 1, 7   (11 = 1011)
# 11:   3, 7      (12 = 1100)
# 12:   0, 3, 7   (13 = 1101)
# 13:   1, 3, 7   (14 = 1110)
# 14:   0, 1, 3, 7 (15 = 1111)

# We need 28 CX gates total - that's the minimum for this structure
# Let me verify this is indeed the minimum by counting connections needed

connections = {
    2: [0, 1],
    4: [0, 3],
    5: [1, 3],
    6: [0, 1, 3],
    8: [0, 7],
    9: [1, 7],
    10: [0, 1, 7],
    11: [3, 7],
    12: [0, 3, 7],
    13: [1, 3, 7],
    14: [0, 1, 3, 7]
}

total_connections = sum(len(v) for v in connections.values())
print(f"Total CX connections needed: {total_connections}")

# The minimum is indeed 28 CX gates
# Let's try to write a more compact version of the circuit

compact_circuit = """H 0 1 3 7
CX 0 2 1 2 0 4 3 4 1 5 3 5 0 6 1 6 3 6 0 8 7 8 1 9 7 9 0 10 1 10 7 10 3 11 7 11 0 12 3 12 7 12 1 13 3 13 7 13 0 14 1 14 3 14 7 14"""

passes_compact, _ = test_circuit(compact_circuit, stabilizers)
cx_compact, h_compact = count_gates(compact_circuit)
print(f"\nCompact circuit: CX={cx_compact}, H={h_compact}, passes={passes_compact}")

# The compact circuit should be equivalent but written more compactly
if passes_compact:
    print("\n=== FINAL OPTIMIZED CIRCUIT ===")
    print(compact_circuit)
