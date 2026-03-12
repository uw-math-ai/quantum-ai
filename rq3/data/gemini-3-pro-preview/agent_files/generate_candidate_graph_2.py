import stim

stabilizers = [
    "XXIIXXIIIIIIIIIIIIIIIIIIIIIIIIIIIII", "IIIIIIIXXIIXXIIIIIIIIIIIIIIIIIIIIII", "IIIIIIIIIIIIIIXXIIXXIIIIIIIIIIIIIII", "IIIIIIIIIIIIIIIIIIIIIXXIIXXIIIIIIII", "IIIIIIIIIIIIIIIIIIIIIIIIIIIIXXIIXXI", "XIXIXIXIIIIIIIIIIIIIIIIIIIIIIIIIIII", "IIIIIIIXIXIXIXIIIIIIIIIIIIIIIIIIIII", "IIIIIIIIIIIIIIXIXIXIXIIIIIIIIIIIIII", "IIIIIIIIIIIIIIIIIIIIIXIXIXIXIIIIIII", "IIIIIIIIIIIIIIIIIIIIIIIIIIIIXIXIXIX", "IIIXXXXIIIIIIIIIIIIIIIIIIIIIIIIIIII", "IIIIIIIIIIXXXXIIIIIIIIIIIIIIIIIIIII", "IIIIIIIIIIIIIIIIIXXXXIIIIIIIIIIIIII", "IIIIIIIIIIIIIIIIIIIIIIIIXXXXIIIIIII", "IIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIXXXX", "ZZIIZZIIIIIIIIIIIIIIIIIIIIIIIIIIIII", "IIIIIIIZZIIZZIIIIIIIIIIIIIIIIIIIIII", "IIIIIIIIIIIIIIZZIIZZIIIIIIIIIIIIIII", "IIIIIIIIIIIIIIIIIIIIIZZIIZZIIIIIIII", "IIIIIIIIIIIIIIIIIIIIIIIIIIIIZZIIZZI", "ZIZIZIZIIIIIIIIIIIIIIIIIIIIIIIIIIII", "IIIIIIIZIZIZIZIIIIIIIIIIIIIIIIIIIII", "IIIIIIIIIIIIIIZIZIZIZIIIIIIIIIIIIII", "IIIIIIIIIIIIIIIIIIIIIZIZIZIZIIIIIII", "IIIIIIIIIIIIIIIIIIIIIIIIIIIIZIZIZIZ", "IIIZZZZIIIIIIIIIIIIIIIIIIIIIIIIIIII", "IIIIIIIIIIZZZZIIIIIIIIIIIIIIIIIIIII", "IIIIIIIIIIIIIIIIIZZZZIIIIIIIIIIIIII", "IIIIIIIIIIIIIIIIIIIIIIIIZZZZIIIIIII", "IIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIZZZZ", "XXXIIIIZZZIIIIZZZIIIIXXXIIIIIIIIIII", "IIIIIIIXXXIIIIZZZIIIIZZZIIIIXXXIIII", "XXXIIIIIIIIIIIXXXIIIIZZZIIIIZZZIIII", "ZZZIIIIXXXIIIIIIIIIIIXXXIIIIZZZIIII"
]

try:
    tableau = stim.Tableau.from_stabilizers([stim.PauliString(s) for s in stabilizers], allow_underconstrained=True)
    circuit = tableau.to_circuit("graph_state")
    
    new_circuit = stim.Circuit()
    for instruction in circuit:
        if instruction.name == "RX":
            new_circuit.append("H", instruction.targets_copy())
        elif instruction.name == "M":
             # Graph state usually adds measurements at the end to verify stabilizers? Or just state prep?
             # If "graph_state" creates a state prep circuit, it might not have measurements.
             # If it has measurements, we might want to keep or remove depending on task.
             # The task is state preparation (stabilizer state), so no measurements at the end.
             # Graph state usually ends with measurements if it's meant to measure stabilizers.
             # But here we want a state prep circuit.
             # Usually method='graph_state' returns a circuit that prepares the state from |0>.
             pass 
        else:
            new_circuit.append(instruction)
            
    print(new_circuit)

except Exception as e:
    print(f"Error: {e}")
