import stim
import sys
import os

def analyze_faults():
    # Use absolute paths or relative to script location
    base_dir = r"C:\Users\anpaz\Repos\quantum-ai\rq2"
    circuit_path = os.path.join(base_dir, "current_circuit.stim")
    ancillas_path = os.path.join(base_dir, "current_ancillas.txt")
    
    with open(circuit_path, "r") as f:
        circuit_str = f.read()
    
    circuit = stim.Circuit(circuit_str)
    
    # Identify data qubits (0-104 based on problem description)
    data_qubits = set(range(105))
    
    # Identify flag qubits
    try:
        with open(ancillas_path, "r") as f:
            ancillas_str = f.read().strip()
            if ancillas_str:
                flag_qubits = set([int(x) for x in ancillas_str.split(",") if x])
            else:
                flag_qubits = set()
    except FileNotFoundError:
        flag_qubits = set()
        
    print(f"Analyzing circuit with {len(circuit)} instructions.")
    print(f"Data qubits: 0-104")
    print(f"Flag qubits: {flag_qubits}")
    
    # Flatten ops
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
        else:
            # Handle other gates if necessary or ignore non-unitary (like TICK)
            pass
                    
    # Find max qubit
    max_q = 0
    if flat_ops:
        for name, targets, _ in flat_ops:
            max_q = max(max_q, max(targets))
    # Ensure at least 105
    total_qubits = max(max_q + 1, 105)
    
    t = stim.Tableau(total_qubits)
    
    severe_faults = []
    
    # Iterate backwards
    # We want to check if a fault inserted AFTER an operation spreads to >3 data qubits at the end.
    
    for i in range(len(flat_ops)-1, -1, -1):
        name, targets, orig_idx = flat_ops[i]
        
        # Check faults at this location (after the gate)
        # Faults: X, Y, Z on each qubit involved in the gate.
        # Actually, faults can happen on any qubit at any time. 
        # But we only care about faults that are "new".
        # Typically we check faults on qubits involved in the operation.
        
        involved = targets
        
        for q in involved:
            for p_type in ["X", "Z"]: # Y is X*Z
                # Check propagation of this Pauli to the output
                res_pauli = t.x_output(q) if p_type == "X" else t.z_output(q)
                
                # Check data weight at the end
                w = 0
                affected_data = []
                for dq in data_qubits:
                    p = res_pauli[dq]
                    if p != 0: # 1=X, 2=Y, 3=Z
                        w += 1
                        affected_data.append(dq)
                
                if w >= 4:
                    # Check flags
                    triggered = False
                    for fq in flag_qubits:
                        p_f = res_pauli[fq]
                        if p_f == 1 or p_f == 2: # X or Y triggers Z-measurement
                            triggered = True
                            break
                    
                    if not triggered:
                        severe_faults.append({
                            "index": i,
                            "orig_idx": orig_idx,
                            "gate": name,
                            "targets": targets,
                            "fault_qubit": q,
                            "fault_type": p_type,
                            "weight": w,
                            "affected": affected_data
                        })
        
        # Update Tableau by PREPENDING the gate (inverse logic)
        # If we go backwards, we are peeling off gates from the end.
        # T_new = T_old * U. (Wait, if T represents circuit from i to end)
        # T_i = U_i * T_{i+1}. 
        # Tableau.prepend does: new_tableau = operation * old_tableau
        # So yes, prepend is correct.
        
        if name not in ["M", "MX", "MY", "MZ", "R", "RX", "RY", "RZ"]:
            t.prepend(stim.Tableau.from_named_gate(name), targets)

    print(f"Found {len(severe_faults)} severe faults.")
    for f in severe_faults[:20]: # Print first 20
        print(f"Op {f['index']} (Line {f['orig_idx']}) {f['gate']} {f['targets']}: Fault {f['fault_type']} on {f['fault_qubit']} -> Weight {f['weight']} {f['affected']}")

if __name__ == "__main__":
    analyze_faults()
