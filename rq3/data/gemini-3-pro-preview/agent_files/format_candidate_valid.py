import stim

def print_circuit_formatted(circuit):
    for instruction in circuit:
        if isinstance(instruction, stim.CircuitInstruction):
            name = instruction.name
            targets = instruction.targets_copy()
            args = instruction.gate_args_copy()
            
            if len(targets) == 0:
                 # e.g. TICK
                 print(name)
                 continue

            # Chunk size
            # For 2-qubit gates, must be even. 
            chunk_size = 20
            
            for i in range(0, len(targets), chunk_size):
                chunk = targets[i:i+chunk_size]
                
                # Format targets
                target_strs = []
                for t in chunk:
                    if t.is_qubit_target:
                        target_strs.append(str(t.value))
                    elif t.is_x_target:
                        target_strs.append(f"X{t.value}")
                    elif t.is_y_target:
                        target_strs.append(f"Y{t.value}")
                    elif t.is_z_target:
                        target_strs.append(f"Z{t.value}")
                    elif t.is_sweep_bit_target:
                         target_strs.append(f"sweep[{t.value}]")
                    elif t.is_measurement_record_target:
                         target_strs.append(f"rec[{t.value}]")
                    
                
                # Format args
                arg_str = ""
                if args:
                    arg_str = "(" + ",".join(str(a) for a in args) + ")"
                
                print(f"{name}{arg_str} {' '.join(target_strs)}")
        else:
             print(str(instruction))

with open("candidate.stim", "r") as f:
    c = stim.Circuit(f.read())

print_circuit_formatted(c)
