import stim

stabilizers = [
    "XXXXIIIIIIIIIIIIIIIIIIIIIIII",
    "IIIIIIIXXXXIIIIIIIIIIIIIIIII",
    "IIIIIIIIIIIIIIXXXXIIIIIIIIII",
    "IIIIIIIIIIIIIIIIIIIIIXXXXIII",
    "XIXIXIXIIIIIIIIIIIIIIIIIIIII",
    "IIIIIIIXIXIXIXIIIIIIIIIIIIII",
    "IIIIIIIIIIIIIIXIXIXIXIIIIIII",
    "IIIIIIIIIIIIIIIIIIIIIXIXIXIX",
    "IIXXXXIIIIIIIIIIIIIIIIIIIIII",
    "IIIIIIIIIXXXXIIIIIIIIIIIIIII",
    "IIIIIIIIIIIIIIIIXXXXIIIIIIII",
    "IIIIIIIIIIIIIIIIIIIIIIIXXXXI",
    "ZZZZIIIIIIIIIIIIIIIIIIIIIIII",
    "IIIIIIIZZZZIIIIIIIIIIIIIIIII",
    "IIIIIIIIIIIIIIZZZZIIIIIIIIII",
    "IIIIIIIIIIIIIIIIIIIIIZZZZIII",
    "ZIZIZIZIIIIIIIIIIIIIIIIIIIII",
    "IIIIIIIZIZIZIZIIIIIIIIIIIIII",
    "IIIIIIIIIIIIIIZIZIZIZIIIIIII",
    "IIIIIIIIIIIIIIIIIIIIIZIZIZIZ",
    "IIZZZZIIIIIIIIIIIIIIIIIIIIII",
    "IIIIIIIIIZZZZIIIIIIIIIIIIIII",
    "IIIIIIIIIIIIIIIIZZZZIIIIIIII",
    "IIIIIIIIIIIIIIIIIIIIIIIZZZZI",
    "IXXIXIIIXXIXIIIXXIXIIIXXIXII",
    "IZZIZIIIZZIZIIIZZIZIIIZZIZII"
]

try:
    tableau = stim.Tableau.from_stabilizers([stim.PauliString(s) for s in stabilizers], allow_underconstrained=True, allow_redundant=True)
    circuit = tableau.to_circuit(method="graph_state")
    
    # Replace RX with H
    final_circuit = stim.Circuit()
    for instruction in circuit:
        if instruction.name == 'RX':
            targets = instruction.targets_copy()
            final_circuit.append('H', targets)
        elif instruction.name == 'TICK':
            pass
        else:
            final_circuit.append(instruction)

    with open('candidate_graph_fixed.stim', 'w') as f:
        f.write(str(final_circuit))

except Exception as e:
    print(f"Error: {e}")
