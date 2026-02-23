import stim

def reformat():
    circuit = stim.Circuit.from_file('data/gemini-3-pro-preview/agent_files/circuit_75.stim')
    
    for instruction in circuit:
        name = instruction.name
        targets = instruction.targets_copy()
        args = instruction.gate_args_copy()
        
        is_two_qubit = name in ['CX', 'CNOT', 'CY', 'CZ', 'SWAP', 'ISWAP', 'SQRT_SWAP']
        
        if is_two_qubit:
            chunk_size = 4
        else:
            chunk_size = 4
            
        if len(targets) > chunk_size:
             for i in range(0, len(targets), chunk_size):
                chunk = targets[i:i+chunk_size]
                # Construct instruction string manually
                # Targets in stim are integers (or objects with properties)
                # But instruction.targets_copy() returns list of stim.GateTarget
                # We need to format them.
                t_strs = []
                for t in chunk:
                    if t.is_x_target: t_strs.append(f'X{t.value}')
                    elif t.is_y_target: t_strs.append(f'Y{t.value}')
                    elif t.is_z_target: t_strs.append(f'Z{t.value}')
                    elif t.is_inverted_result_target: t_strs.append(f'!{t.value}')
                    elif t.is_measurement_record_target: t_strs.append(f'rec[{t.value}]')
                    else: t_strs.append(str(t.value))
                
                print(f"{name} {' '.join(t_strs)}")
        else:
            # Just print the instruction as is
            print(instruction)

if __name__ == '__main__':
    reformat()
