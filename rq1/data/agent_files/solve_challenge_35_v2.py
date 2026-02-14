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
    pauli_strings = [stim.PauliString(s) for s in stabilizers_str]
    t = stim.Tableau.from_stabilizers(pauli_strings, allow_underconstrained=True, allow_redundant=True)
    circuit = t.to_circuit()
    
    print("CIRCUIT_START")
    for instruction in circuit:
        name = instruction.name
        targets = []
        for t in instruction.targets_copy():
            if t.is_qubit_target:
                targets.append(str(t.value))
            elif t.is_x_target:
                targets.append(f"X{t.value}")
            elif t.is_y_target:
                targets.append(f"Y{t.value}")
            elif t.is_z_target:
                targets.append(f"Z{t.value}")
            elif t.is_combiner:
                targets.append("*")
            else:
                targets.append(str(t))
        
        gate_args = ""
        if instruction.gate_args_copy():
            gate_args = "(" + ",".join(map(str, instruction.gate_args_copy())) + ")"
            
        # Chunking to avoid line wrapping
        # We'll use a chunk size of 8 targets (and respect pairs for 2-qubit gates)
        
        is_two_qubit_gate = name in ["CX", "CY", "CZ", "SWAP", "ISWAP", "CXSWAP", "SWAPCX", "SQRT_ZZ", "SQRT_XX", "SQRT_YY", "MXX", "MZZ", "MYY"]
        step = 2 if is_two_qubit_gate else 1
        chunk_size = 10 * step
        
        if len(targets) > chunk_size:
            for i in range(0, len(targets), chunk_size):
                chunk = targets[i : i + chunk_size]
                if chunk:
                    print(f"{name}{gate_args} {' '.join(chunk)}")
        else:
            print(f"{name}{gate_args} {' '.join(targets)}")
            
    print("CIRCUIT_END")
    
except Exception as e:
    print(f"Error: {e}")
