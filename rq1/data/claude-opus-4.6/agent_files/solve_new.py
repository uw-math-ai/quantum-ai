import stim

# Define stabilizers for this task (20 qubits)
stabilizers = [
    "XZZXIIIIIIIIIIIIIIII",
    "IIIIIXZZXIIIIIIIIIII",
    "IIIIIIIIIIXZZXIIIIII",
    "IIIIIIIIIIIIIIIXZZXI",
    "IXZZXIIIIIIIIIIIIIII",
    "IIIIIIXZZXIIIIIIIIII",
    "IIIIIIIIIIIXZZXIIIII",
    "IIIIIIIIIIIIIIIIXZZX",
    "XIXZZIIIIIIIIIIIIIII",
    "IIIIIXIXZZIIIIIIIIII",
    "IIIIIIIIIIXIXZZIIIII",
    "IIIIIIIIIIIIIIIXIXZZ",
    "ZXIXZIIIIIIIIIIIIIII",
    "IIIIIZXIXZIIIIIIIIII",
    "IIIIIIIIIIZXIXZIIIII",
    "IIIIIIIIIIIIIIIZXIXZ",
    "XXXXXXXXXXXXXXXXXXXX",
    "ZZZZZZZZZZZZZZZZZZZZ",
]

n_qubits = 20
print(f"Number of stabilizers: {len(stabilizers)}")
print(f"Number of qubits: {n_qubits}")

# Convert stabilizer strings to stim.PauliString
pauli_strings = []
for s in stabilizers:
    pauli_strings.append(stim.PauliString(s))

# Check if they all commute
print("\nChecking commutativity...")
anticommute_pairs = []
for i, p1 in enumerate(pauli_strings):
    for j, p2 in enumerate(pauli_strings):
        if i < j:
            if not p1.commutes(p2):
                anticommute_pairs.append((i, j))
                print(f"Stabilizers {i} and {j} anticommute!")

if not anticommute_pairs:
    print("All stabilizers commute!")

# Try to build a tableau from stabilizers
print("\nBuilding tableau from stabilizers...")
try:
    tableau = stim.Tableau.from_stabilizers(
        pauli_strings,
        allow_redundant=True,
        allow_underconstrained=True
    )
    print(f"Tableau created successfully with {len(tableau)} qubits")
    
    # Generate circuit using graph_state method (produces CZ gates, CX=0)
    circuit = tableau.to_circuit(method='graph_state')
    print(f"\nGenerated circuit with {len(circuit)} instructions")
    
    # Clean up RX gates (replace with H for starting from |0>)
    clean_lines = []
    for inst in circuit:
        name = inst.name
        if name == "RX":
            targets = inst.targets_copy()
            for t in targets:
                clean_lines.append(f"H {t.value}")
        else:
            clean_lines.append(str(inst))
    
    clean_circuit = stim.Circuit("\n".join(clean_lines))
    print(f"Cleaned circuit:\n{clean_circuit}")
    
    # Count gates
    cx_count = 0
    cz_count = 0
    volume = 0
    for inst in clean_circuit:
        name = inst.name
        if name == "CX" or name == "CNOT":
            cx_count += len(inst.targets_copy()) // 2
        elif name == "CZ":
            cz_count += len(inst.targets_copy()) // 2
        if name not in ["TICK", "DETECTOR", "OBSERVABLE_INCLUDE"]:
            if name in ["CX", "CZ", "CY", "SWAP", "ISWAP"]:
                volume += len(inst.targets_copy()) // 2
            else:
                volume += len(inst.targets_copy())
    
    print(f"\nGate counts: CX={cx_count}, CZ={cz_count}, Volume={volume}")
    
    # Save the circuit
    with open("data/claude-opus-4.6/agent_files/candidate_new.stim", "w") as f:
        f.write(str(clean_circuit))
    
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
