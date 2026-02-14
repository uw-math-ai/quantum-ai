import stim

stabilizers_str = [
    "XXXXIIIIIIIIIIIIIIIIIIIIIIIIIIIIIII", 
    "IIIIIIIXXXXIIIIIIIIIIIIIIIIIIIIIIII", 
    "IIIIIIIIIIIIIIXXXXIIIIIIIIIIIIIIIII", 
    "IIIIIIIIIIIIIIIIIIIIIXXXXIIIIIIIIII", 
    "IIIIIIIIIIIIIIIIIIIIIIIIIIIIXXXXIII", 
    "XIXIXIXIIIIIIIIIIIIIIIIIIIIIIIIIIII", 
    "IIIIIIIXIXIXIXIIIIIIIIIIIIIIIIIIIII", 
    "IIIIIIIIIIIIIIXIXIXIXIIIIIIIIIIIIII", 
    "IIIIIIIIIIIIIIIIIIIIIXIXIXIXIIIIIII", 
    "IIIIIIIIIIIIIIIIIIIIIIIIIIIIXIXIXIX", 
    "IIXXXXIIIIIIIIIIIIIIIIIIIIIIIIIIIII", 
    "IIIIIIIIIXXXXIIIIIIIIIIIIIIIIIIIIII", 
    "IIIIIIIIIIIIIIIIXXXXIIIIIIIIIIIIIII", 
    "IIIIIIIIIIIIIIIIIIIIIIIXXXXIIIIIIII", 
    "IIIIIIIIIIIIIIIIIIIIIIIIIIIIIIXXXXI", 
    "ZZZZIIIIIIIIIIIIIIIIIIIIIIIIIIIIIII", 
    "IIIIIIIZZZZIIIIIIIIIIIIIIIIIIIIIIII", 
    "IIIIIIIIIIIIIIZZZZIIIIIIIIIIIIIIIII", 
    "IIIIIIIIIIIIIIIIIIIIIZZZZIIIIIIIIII", 
    "IIIIIIIIIIIIIIIIIIIIIIIIIIIIZZZZIII", 
    "ZIZIZIZIIIIIIIIIIIIIIIIIIIIIIIIIIII", 
    "IIIIIIIZIZIZIZIIIIIIIIIIIIIIIIIIIII", 
    "IIIIIIIIIIIIIIZIZIZIZIIIIIIIIIIIIII", 
    "IIIIIIIIIIIIIIIIIIIIIZIZIZIZIIIIIII", 
    "IIIIIIIIIIIIIIIIIIIIIIIIIIIIZIZIZIZ", 
    "IIZZZZIIIIIIIIIIIIIIIIIIIIIIIIIIIII", 
    "IIIIIIIIIZZZZIIIIIIIIIIIIIIIIIIIIII", 
    "IIIIIIIIIIIIIIIIZZZZIIIIIIIIIIIIIII", 
    "IIIIIIIIIIIIIIIIIIIIIIIZZZZIIIIIIII", 
    "IIIIIIIIIIIIIIIIIIIIIIIIIIIIIIZZZZI", 
    "IXXIXIIIZZIZIIIZZIZIIIXXIXIIIIIIIII", 
    "IIIIIIIIXXIXIIIZZIZIIIZZIZIIIXXIXII", 
    "IXXIXIIIIIIIIIIXXIXIIIZZIZIIIZZIZII", 
    "IZZIZIIIXXIXIIIIIIIIIIXXIXIIIZZIZII"
]

try:
    # Check if we have the right number of qubits (35)
    # The strings are length 35.
    
    pauli_strings = [stim.PauliString(s) for s in stabilizers_str]
    
    # We create a Tableau.
    # allow_underconstrained=True because we have 34 stabs for 35 qubits.
    # allow_redundant=True just in case.
    t = stim.Tableau.from_stabilizers(pauli_strings, allow_underconstrained=True, allow_redundant=True)
    
    # Convert to circuit
    circuit = t.to_circuit()
    
    # Print the circuit
    print("CIRCUIT_START")
    # Manually format to avoid wrapping
    for instruction in circuit:
        name = instruction.name
        args = []
        for t in instruction.targets_copy():
            if t.is_qubit_target:
                args.append(str(t.value))
            elif t.is_x_target:
                args.append(f"X{t.value}")
            elif t.is_y_target:
                args.append(f"Y{t.value}")
            elif t.is_z_target:
                args.append(f"Z{t.value}")
            elif t.is_combiner:
                args.append("*")
            else:
                args.append(str(t))
        
        gate_args = ""
        if instruction.gate_args_copy():
            gate_args = "(" + ",".join(map(str, instruction.gate_args_copy())) + ")"

        print(f"{name}{gate_args} {' '.join(args)}")
    print("CIRCUIT_END")
    
except Exception as e:
    print(f"Error: {e}")
