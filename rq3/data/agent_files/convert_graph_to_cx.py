import stim

def convert():
    circuit = stim.Circuit.from_file("candidate_graph.stim")
    new_circuit = stim.Circuit()
    
    for instr in circuit:
        if instr.name == "CZ":
            targets = instr.targets_copy()
            for k in range(0, len(targets), 2):
                u = targets[k]
                v = targets[k+1]
                
                # Decompose CZ(u, v) -> H(v) CX(u, v) H(v)
                # Note: u and v are target objects, need values
                u_val = u.value
                v_val = v.value
                
                new_circuit.append("H", [v_val])
                new_circuit.append("CX", [u_val, v_val])
                new_circuit.append("H", [v_val])
        else:
            new_circuit.append(instr)
            
    cx_count = 0
    for instr in new_circuit:
        if instr.name == "CX":
            cx_count += len(instr.targets_copy()) // 2
            
    print(f"Converted circuit has {cx_count} CX gates.")
    new_circuit.to_file("candidate_final.stim")

if __name__ == "__main__":
    convert()
