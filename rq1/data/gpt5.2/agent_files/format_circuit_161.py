import stim

def format_circuit():
    with open("circuit_161.stim", "r") as f:
        content = f.read()
    
    circuit = stim.Circuit(content)
    # Print each instruction on a new line, breaking down long ones
    for instruction in circuit:
        gate = instruction.name
        targets = instruction.targets_copy()
        args = instruction.gate_args_copy()
        
        # Format args string (e.g. for noisy gates, not relevant for CX/H/etc here but good practice)
        args_str = ""
        if args:
            args_str = "(" + ",".join(str(a) for a in args) + ")"

        # Process targets
        # Most gates take 1 target per operation (H, X, Z, M, R)
        # 2-qubit gates take 2 targets per operation (CX, CZ, SWAP)
        # We assume standard gates here.
        
        is_two_qubit = gate in ["CX", "CY", "CZ", "SWAP", "ISWAP", "SQRT_XX", "SQRT_YY", "SQRT_ZZ"]
        step = 2 if is_two_qubit else 1
        
        for i in range(0, len(targets), step):
            chunk = targets[i:i+step]
            # Convert targets to string (handling combiners/paulis if any, but unlikely for stabilizer prep)
            # For simple stabilizer circuits, targets are just qubit indices.
            t_strs = []
            for t in chunk:
                if t.is_qubit_target:
                    t_strs.append(str(t.value))
                elif t.is_combiner:
                    t_strs.append("*")
                elif t.is_x_target:
                    t_strs.append(f"X{t.value}")
                elif t.is_y_target:
                    t_strs.append(f"Y{t.value}")
                elif t.is_z_target:
                    t_strs.append(f"Z{t.value}")
                elif t.is_sweep_bit_target:
                    t_strs.append(f"sweep[{t.value}]")
                elif t.is_measurement_record_target:
                    t_strs.append(f"rec[{t.value}]")
            
            print(f"{gate}{args_str} {' '.join(t_strs)}")

if __name__ == "__main__":
    format_circuit()
