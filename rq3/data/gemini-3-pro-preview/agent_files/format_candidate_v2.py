import stim

# Use Stim's gate data to detect arity if possible, or just hardcode
arity_map = {
    "CX": 2, "CY": 2, "CZ": 2, "CNOT": 2, "SWAP": 2, "ISWAP": 2,
    "H": 1, "S": 1, "S_DAG": 1, "X": 1, "Y": 1, "Z": 1, "SQRT_X": 1, "SQRT_Y": 1, "SQRT_Z": 1,
    "RX": 1, "RY": 1, "RZ": 1, "M": 1, "MX": 1, "MY": 1, "MZ": 1,
    "TICK": 0, "SHIFT_COORDS": 0, "QUBIT_COORDS": 0, "DETECTOR": 0, "OBSERVABLE_INCLUDE": 0
}

c = stim.Circuit.from_file("candidate_final_submission.stim")

def target_to_str(t):
    if t.is_combiner:
        return "*"
    if t.is_x_target:
        return f"X{t.value}"
    if t.is_y_target:
        return f"Y{t.value}"
    if t.is_z_target:
        return f"Z{t.value}"
    if t.is_inverted_result_target:
        return f"!{t.value}"
    if t.is_measurement_record_target:
        return f"rec[{t.value}]"
    if t.is_sweep_bit_target:
        return f"sweep[{t.value}]"
    return str(t.value)

with open("candidate_formatted.stim", "w") as f:
    for op in c:
        name = op.name
        targets = op.targets_copy()
        arity = arity_map.get(name, 1) # Default to 1
        
        if arity == 0:
            if name == "TICK":
                 f.write(f"{name}\n")
            else:
                 f.write(str(op) + "\n")
            continue
            
        # Process targets in chunks of arity * k
        # Keep lines short. Say 10 args max.
        k = 5
        chunk_len = arity * k
        
        if len(targets) == 0:
             f.write(str(op) + "\n")
             continue

        for i in range(0, len(targets), chunk_len):
            chunk = targets[i:i+chunk_len]
            # Construct instruction string manually
            args = []
            for t in chunk:
                args.append(target_to_str(t))
            if args:
                f.write(f"{name} {' '.join(args)}\n")
