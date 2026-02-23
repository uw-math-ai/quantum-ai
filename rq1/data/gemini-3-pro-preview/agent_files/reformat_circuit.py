import stim

def reformat_circuit():
    input_file = r'C:\Users\anpaz\Repos\quantum-ai\rq1\data\gemini-3-pro-preview\agent_files\circuit.stim'
    output_file = r'C:\Users\anpaz\Repos\quantum-ai\rq1\data\gemini-3-pro-preview\agent_files\circuit_clean.stim'
    
    with open(input_file, 'r') as f:
        content = f.read()
        
    circuit = stim.Circuit(content)
    
    # Repopulate the string without line wrapping issues if possible
    # stim's str() wraps long lines.
    # We can iterate instructions and print them one per line.
    
    with open(output_file, 'w') as f:
        for instruction in circuit:
            name = instruction.name
            targets = instruction.targets_copy()
            # targets contains stim.GateTarget objects
            # we need to convert them to strings like "0" or "comb(0, 1)"
            # For simple qubit targets, .value is the qubit index.
            # .is_x_target, .is_y_target etc...
            
            target_strs = []
            for t in instruction.targets_copy():
                if t.is_combiner:
                    target_strs.append("comb")
                elif t.is_x_target:
                    target_strs.append(f"X{t.value}")
                elif t.is_y_target:
                    target_strs.append(f"Y{t.value}")
                elif t.is_z_target:
                    target_strs.append(f"Z{t.value}")
                elif t.is_inverted_result_target:
                    target_strs.append(f"!{t.value}")
                elif t.is_measurement_record_target:
                    target_strs.append(f"rec[{t.value}]")
                else:
                    target_strs.append(str(t.value))
                
            line = f"{instruction.name} {' '.join(target_strs)}"
            f.write(line + '\n')
            
    print(f"Reformatted circuit to {output_file}")

if __name__ == "__main__":
    reformat_circuit()
