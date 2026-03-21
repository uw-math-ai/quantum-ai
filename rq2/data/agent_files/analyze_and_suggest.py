import stim
import sys
import os
import collections

def analyze_and_suggest():
    base_dir = r"C:\Users\anpaz\Repos\quantum-ai\rq2"
    circuit_path = os.path.join(base_dir, "current_circuit.stim")
    ancillas_path = os.path.join(base_dir, "current_ancillas.txt")
    stabilizers_path = os.path.join(base_dir, "stabilizers.txt")
    
    with open(circuit_path, "r") as f:
        circuit_str = f.read()
    circuit = stim.Circuit(circuit_str)
    
    with open(stabilizers_path, "r") as f:
        stabs_lines = f.readlines()
    stabilizers = [stim.PauliString(s.strip()) for s in stabs_lines if s.strip()]
    
    data_qubits = set(range(105))
    try:
        with open(ancillas_path, "r") as f:
            ancillas_str = f.read().strip()
            if ancillas_str:
                flag_qubits = set([int(x) for x in ancillas_str.split(",") if x])
            else:
                flag_qubits = set()
    except FileNotFoundError:
        flag_qubits = set()
        
    flat_ops = []
    for i, instr in enumerate(circuit):
        if instr.name in ["H", "CX", "S", "X", "Y", "Z", "I", "M", "R", "RX", "RY", "RZ", "MX", "MY", "MZ"]:
            targets = instr.targets_copy()
            if instr.name == "CX":
                for k in range(0, len(targets), 2):
                    flat_ops.append((instr.name, [targets[k].value, targets[k+1].value], i))
            elif instr.name in ["M", "MX", "MY", "MZ", "R", "RX", "RY", "RZ"]:
                 for t in targets:
                    flat_ops.append((instr.name, [t.value], i))
            else:
                for t in targets:
                    flat_ops.append((instr.name, [t.value], i))
    
    max_q = 0
    if flat_ops:
        for name, targets, _ in flat_ops:
            max_q = max(max_q, max(targets))
    total_qubits = max(max_q + 1, 105)
    
    t = stim.Tableau(total_qubits)
    
    severe_faults = []
    
    print("Finding faults...")
    for i in range(len(flat_ops)-1, -1, -1):
        name, targets, orig_idx = flat_ops[i]
        involved = targets
        
        for q in involved:
            for p_type in ["X", "Z"]: 
                res_pauli = t.x_output(q) if p_type == "X" else t.z_output(q)
                
                w = 0
                for dq in data_qubits:
                    p = res_pauli[dq]
                    if p != 0:
                        w += 1
                
                if w >= 4:
                    triggered = False
                    for fq in flag_qubits:
                        p_f = res_pauli[fq]
                        if p_f == 1 or p_f == 2:
                            triggered = True
                            break
                    
                    if not triggered:
                        # Check detecting stabilizers
                        detecting = []
                        for s_idx, stab in enumerate(stabilizers):
                            # Commutativity check
                            # res_pauli is a PauliString with length total_qubits.
                            # stab is length 105.
                            # We need to slice res_pauli to 105 or pad stab?
                            # Usually pad stab with I.
                            
                            # Construct full length stab
                            full_stab = stim.PauliString(total_qubits)
                            for k in range(105):
                                full_stab[k] = stab[k]
                            
                            if not full_stab.commutes(res_pauli):
                                detecting.append(s_idx)
                        
                        severe_faults.append({
                            'index': i,
                            'weight': w,
                            'detecting': detecting
                        })
        
        if name not in ["M", "MX", "MY", "MZ", "R", "RX", "RY", "RZ"]:
            t.prepend(stim.Tableau.from_named_gate(name), targets)

    print(f"Found {len(severe_faults)} severe faults.")
    
    # Greedy set cover
    uncovered = set(range(len(severe_faults)))
    selected_stabilizers = []
    
    while uncovered:
        counts = collections.Counter()
        for f_idx in uncovered:
            for s_idx in severe_faults[f_idx]['detecting']:
                counts[s_idx] += 1
        
        if not counts:
            print("Some faults are undetectable by any stabilizer!")
            # Inspect first undetectable
            first_idx = list(uncovered)[0]
            print(f"Undetectable fault weight {severe_faults[first_idx]['weight']}")
            # Remove them from uncovered to continue finding cover for others
            new_uncovered = set()
            for f_idx in uncovered:
                if not severe_faults[f_idx]['detecting']:
                    pass # skip
                else:
                    new_uncovered.add(f_idx)
            if len(new_uncovered) == len(uncovered):
                 break # Loop
            uncovered = new_uncovered
            continue
            
        best_s = counts.most_common(1)[0][0]
        selected_stabilizers.append(best_s)
        
        new_uncovered = set()
        for f_idx in uncovered:
            if best_s not in severe_faults[f_idx]['detecting']:
                new_uncovered.add(f_idx)
        uncovered = new_uncovered
        
    print(f"Selected {len(selected_stabilizers)} stabilizers.")
    for s_idx in selected_stabilizers:
        print(f"Stab {s_idx}: {stabilizers[s_idx]}")

if __name__ == "__main__":
    analyze_and_suggest()
