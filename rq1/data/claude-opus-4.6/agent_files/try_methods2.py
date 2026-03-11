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

pauli_strings = [stim.PauliString(s) for s in stabilizers]

# Try different methods
methods = ['graph_state', 'elimination']

for method in methods:
    print(f"\n=== Method: {method} ===")
    try:
        tableau = stim.Tableau.from_stabilizers(
            pauli_strings,
            allow_redundant=True,
            allow_underconstrained=True
        )
        circuit = tableau.to_circuit(method=method)
        
        # Clean up RX gates
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
        
        print(f"CX={cx_count}, CZ={cz_count}, Volume={volume}")
        print(f"Circuit:\n{clean_circuit}")
        
        # Save if it's the elimination method
        if method == 'elimination':
            with open("data/claude-opus-4.6/agent_files/candidate_elim.stim", "w") as f:
                f.write(str(clean_circuit))
    except Exception as e:
        print(f"Error: {e}")
