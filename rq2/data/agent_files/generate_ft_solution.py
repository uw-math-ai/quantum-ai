import stim
import sys
import os
import collections

def generate_solution():
    base_dir = r"C:\Users\anpaz\Repos\quantum-ai\rq2"
    circuit_path = os.path.join(base_dir, "current_circuit.stim")
    ancillas_path = os.path.join(base_dir, "ancillas.txt") # Output file
    stabilizers_path = os.path.join(base_dir, "stabilizers.txt")
    output_circuit_path = os.path.join(base_dir, "solution.stim")
    
    with open(circuit_path, "r") as f:
        circuit_str = f.read()
    circuit = stim.Circuit(circuit_str)
    
    with open(stabilizers_path, "r") as f:
        stabs_lines = f.readlines()
    stabilizers = [stim.PauliString(s.strip()) for s in stabs_lines if s.strip()]
    
    data_qubits = set(range(105))
    
    # Analyze faults (Simplified re-implementation)
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
    severe_faults = [] # Store detecting stabilizers indices
    
    print("Analyzing faults...")
    for i in range(len(flat_ops)-1, -1, -1):
        name, targets, orig_idx = flat_ops[i]
        involved = targets
        for q in involved:
            for p_type in ["X", "Z"]: 
                res_pauli = t.x_output(q) if p_type == "X" else t.z_output(q)
                w = 0
                for dq in data_qubits:
                    if res_pauli[dq] != 0:
                        w += 1
                
                if w >= 4:
                    detecting = []
                    # Check commutativity
                    # Optimization: only check if w >= 4
                    for s_idx, stab in enumerate(stabilizers):
                        # Pad stab to total_qubits
                        full_stab = stim.PauliString(total_qubits)
                        for k in range(105):
                            full_stab[k] = stab[k]
                        if not full_stab.commutes(res_pauli):
                            detecting.append(s_idx)
                    
                    if detecting:
                        severe_faults.append(detecting)
                    # If detecting is empty, it's undetectable (weight 4 stabilizer or logical)
                    # We ignore for now as we can't do anything without changing circuit structure.
        
        if name not in ["M", "MX", "MY", "MZ", "R", "RX", "RY", "RZ"]:
            t.prepend(stim.Tableau.from_named_gate(name), targets)

    print(f"Found {len(severe_faults)} detectable severe faults.")

    # Greedy set cover
    uncovered = set(range(len(severe_faults)))
    selected_stabilizers = []
    
    while uncovered:
        counts = collections.Counter()
        for f_idx in uncovered:
            for s_idx in severe_faults[f_idx]:
                counts[s_idx] += 1
        
        if not counts:
            break
            
        best_s = counts.most_common(1)[0][0]
        selected_stabilizers.append(best_s)
        
        new_uncovered = set()
        for f_idx in uncovered:
            if best_s not in severe_faults[f_idx]:
                new_uncovered.add(f_idx)
        uncovered = new_uncovered

    print(f"Selected {len(selected_stabilizers)} stabilizers.")

    # Generate circuit with measurements
    new_circuit = circuit.copy()
    ancilla_start = 105
    all_new_ancillas = []
    
    for s_idx in selected_stabilizers:
        stab = stabilizers[s_idx]
        
        support = []
        is_x = False
        is_z = False
        for k in range(105):
            p = stab[k]
            if p == 1: # X
                is_x = True
                support.append(k)
            elif p == 3: # Z
                is_z = True
                support.append(k)
        
        if not support:
            continue
            
        # Determine chunk size.
        # Max weight unflagged should be < 4.
        # If we have CX A q1, CX A q2, CX A q3.
        # Fault on A spreads to q1, q2, q3 (weight 3). Safe.
        # So chunk size 3 is safe.
        chunk_size = 3
        chunks = [support[i:i + chunk_size] for i in range(0, len(support), chunk_size)]
        
        # Allocate Ancilla
        main_anc = ancilla_start
        ancilla_start += 1
        all_new_ancillas.append(main_anc)
        
        # Allocate Flags
        # We need a flag after each chunk except the last one.
        # Actually, even the last one? No.
        flags = []
        for _ in range(len(chunks) - 1):
            f = ancilla_start
            ancilla_start += 1
            all_new_ancillas.append(f)
            flags.append(f)
            
        if is_x:
            # X-stabilizer (measures X ops on data)
            # Uses Main in |+>.
            # Gates: CX Main Data.
            # Flags: Check Z on Main.
            
            new_circuit.append("H", [main_anc])
            for f in flags:
                new_circuit.append("H", [f])
            
            for i, chunk in enumerate(chunks):
                for q in chunk:
                    new_circuit.append("CX", [main_anc, q])
                
                if i < len(chunks) - 1:
                    flag = flags[i]
                    # Detect Z on Main: CX Flag Main (Flag in |+>, Main Target)
                    new_circuit.append("CX", [flag, main_anc])
            
            new_circuit.append("H", [main_anc])
            for f in flags:
                new_circuit.append("H", [f])

        elif is_z:
            # Z-stabilizer (measures Z ops on data)
            # Uses Main in |0>.
            # Gates: CX Data Main.
            # Flags: Check X on Main.
            
            # Flags start in |0> (default)
            
            for i, chunk in enumerate(chunks):
                for q in chunk:
                    new_circuit.append("CX", [q, main_anc])
                
                if i < len(chunks) - 1:
                    flag = flags[i]
                    # Detect X on Main: CX Main Flag (Main Control, Flag Target)
                    new_circuit.append("CX", [main_anc, flag])
                    
            # Measurements in Z basis (default)
            
    # Measure all new ancillas
    new_circuit.append("M", all_new_ancillas)
    
    with open(output_circuit_path, "w") as f:
        f.write(str(new_circuit))
        
    with open(ancillas_path, "w") as f:
        f.write(",".join(map(str, all_new_ancillas)))
        
    print(f"Generated solution with {len(all_new_ancillas)} ancillas.")

if __name__ == "__main__":
    generate_solution()
