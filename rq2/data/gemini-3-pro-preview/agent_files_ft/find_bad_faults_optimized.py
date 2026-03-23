import stim
import json
import sys

def find_bad_faults():
    circuit = stim.Circuit.from_file(r"C:\Users\anpaz\Repos\quantum-ai\rq2\data\gemini-3-pro-preview\agent_files_ft\circuit.stim")
    num_qubits = circuit.num_qubits
    threshold = (9 - 1) // 2  # 4
    
    # Flatten ops
    ops_list = []
    for op in circuit:
        if op.name == "CX" or op.name == "CNOT":
            t = op.targets_copy()
            for k in range(0, len(t), 2):
                ops_list.append( ("CX", [t[k].value, t[k+1].value]) )
        elif op.name in ["H", "X", "Y", "Z", "I"]:
            t = op.targets_copy()
            for k in t:
                ops_list.append( (op.name, [k.value]) )
        else:
            # Keep other ops but maybe warn?
            # Assuming only Clifford gates affect propagation relevant to us
            ops_list.append( (op.name, [k.value for k in op.targets_copy()]) )
            
    print(f"Flattened ops length: {len(ops_list)}")
    
    # Initialize Tableau as Identity (representing empty suffix)
    T = stim.Tableau(num_qubits)
    
    bad_faults = []
    
    # Iterate backwards
    for i in range(len(ops_list) - 1, -1, -1):
        name, targets = ops_list[i]
        
        # Check faults *after* this gate (which propagate through T)
        # Only for CX and H
        if name in ["CX", "CNOT", "H", "X", "Y", "Z"]:
            # Targets are integers now
            for q in targets:
                for p_type in ["X", "Z"]:
                    p = stim.PauliString(num_qubits)
                    if p_type == "X":
                        p[q] = "X"
                    else:
                        p[q] = "Z"
                    
                    # Propagate through suffix (T)
                    res = T(p)
                    w = res.weight
                    
                    if w >= threshold:
                        bad_faults.append({
                            "op_index": i,
                            "gate": name,
                            "targets": targets,
                            "fault_type": p_type,
                            "qubit": q,
                            "weight": w
                        })

        # Update Tableau: prepend this gate
        # T_new = T_old . Gate
        # Stim methods: prepend_...
        if name == "CX" or name == "CNOT":
            # For multi-target CX, we flattened it.
            # Here targets is [c, t]
            T.prepend_cnot(targets[0], targets[1])
        elif name == "H":
            T.prepend_h(targets[0])
        elif name == "X":
            T.prepend_x(targets[0])
        elif name == "Y":
            T.prepend_y(targets[0])
        elif name == "Z":
            T.prepend_z(targets[0])
        # Ignore others or handle if needed
        
    print(f"Found {len(bad_faults)} bad faults.")
    
    # Save to file
    with open(r"C:\Users\anpaz\Repos\quantum-ai\rq2\data\gemini-3-pro-preview\agent_files_ft\bad_faults.json", "w") as f:
        json.dump(bad_faults, f, indent=2)

if __name__ == "__main__":
    find_bad_faults()
