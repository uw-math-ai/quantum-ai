import stim
import sys

def fix(input_path, output_path):
    with open(input_path, 'r') as f:
        circuit_text = f.read()
    circuit = stim.Circuit(circuit_text)
    
    # Pass 1: Same Control
    circ_1 = stim.Circuit()
    
    # Helper to scan for max q
    max_q = 48
    for op in circuit.flattened():
        for t in op.targets_copy():
            if t.is_qubit_target:
                max_q = max(max_q, t.value)
    
    next_ancilla = max_q + 1
    used_ancillas = []
    
    pending_cx = [] 
    
    def process_pending_control(cx_list, circ, anc_idx):
        i = 0
        while i < len(cx_list):
            c = cx_list[i][0]
            j = i + 1
            while j < len(cx_list) and cx_list[j][0] == c:
                j += 1
            
            group = cx_list[i:j]
            targets = [x[1] for x in group]
            
            if len(targets) >= 2:
                flag = anc_idx
                used_ancillas.append(flag)
                anc_idx += 1
                
                circ.append("CX", [c, flag])
                for t in targets:
                    circ.append("CX", [c, t])
                circ.append("CX", [c, flag])
            else:
                for t in targets:
                    circ.append("CX", [c, t])
            i = j
        return anc_idx

    # Pass 1
    ops = list(circuit.flattened())
    for op in ops:
        if op.name == "CX":
            targs = op.targets_copy()
            for k in range(0, len(targs), 2):
                c = targs[k].value
                t = targs[k+1].value
                pending_cx.append((c, t))
        else:
            if pending_cx:
                next_ancilla = process_pending_control(pending_cx, circ_1, next_ancilla)
                pending_cx = []
            circ_1.append(op)
    if pending_cx:
        next_ancilla = process_pending_control(pending_cx, circ_1, next_ancilla)

    # Pass 2: Same Target (Phase Flag)
    circ_2 = stim.Circuit()
    pending_cx = []
    
    def process_pending_target(cx_list, circ, anc_idx):
        i = 0
        while i < len(cx_list):
            t = cx_list[i][1]
            j = i + 1
            while j < len(cx_list) and cx_list[j][1] == t:
                j += 1
            
            group = cx_list[i:j]
            controls = [x[0] for x in group]
            
            if len(controls) >= 2:
                flag = anc_idx
                used_ancillas.append(flag)
                anc_idx += 1
                
                circ.append("H", [flag])
                circ.append("CX", [flag, t]) # Control flag
                for c in controls:
                    circ.append("CX", [c, t])
                circ.append("CX", [flag, t])
                circ.append("H", [flag])
            else:
                for c in controls:
                    circ.append("CX", [c, t])
            i = j
        return anc_idx

    # Pass 2
    ops_1 = list(circ_1.flattened())
    for op in ops_1:
        if op.name == "CX":
            targs = op.targets_copy()
            for k in range(0, len(targs), 2):
                c = targs[k].value
                t = targs[k+1].value
                pending_cx.append((c, t))
        else:
            if pending_cx:
                next_ancilla = process_pending_target(pending_cx, circ_2, next_ancilla)
                pending_cx = []
            circ_2.append(op)
    if pending_cx:
        next_ancilla = process_pending_target(pending_cx, circ_2, next_ancilla)
        
    # Measurements
    if used_ancillas:
        # Sort to keep deterministic
        used_ancillas.sort()
        circ_2.append("M", used_ancillas)
        
    with open(output_path, 'w') as f:
        f.write(str(circ_2))
        
    print(f"Fixed circuit written to {output_path}. Used {len(used_ancillas)} flags.")

if __name__ == "__main__":
    fix("candidate_initial.stim", "candidate_fixed_v2.stim")
