import stim
import collections

def analyze_faults(circuit_path):
    try:
        with open(circuit_path, 'r') as f:
            circuit_str = f.read()
    except Exception as e:
        print(f"Error reading {circuit_path}: {e}")
        return

    try:
        circuit = stim.Circuit(circuit_str)
    except Exception as e:
        print(f"Error parsing circuit: {e}")
        return

    # Force 81 qubits
    num_qubits = max(circuit.num_qubits, 81)
    
    ops = list(circuit)
    
    print(f"Analyzing {len(ops)} operations on {num_qubits} qubits...")
    
    bad_faults = []
    
    current_tableau = stim.Tableau(num_qubits)
    
    for i in range(len(ops) - 1, -1, -1):
        op = ops[i]
        
        targets = []
        for t in op.targets_copy():
            if t.is_qubit_target:
                targets.append(t.value)
        
        for q in targets:
            for p_name in ["X", "Y", "Z"]:
                x_out = current_tableau.x_output(q)
                z_out = current_tableau.z_output(q)
                
                final_pauli = None
                if p_name == "X":
                    final_pauli = x_out
                elif p_name == "Z":
                    final_pauli = z_out
                elif p_name == "Y":
                    final_pauli = x_out * z_out
                
                w = 0
                s = str(final_pauli)
                # s format: "+_XZ..."
                for k in range(81):
                    if k+1 < len(s): 
                        if s[k+1] != '_':
                            w += 1
                
                if w >= 4:
                    bad_faults.append({
                        "op_index": i,
                        "qubit": q,
                        "type": p_name,
                        "weight": w,
                        "op_name": op.name
                    })
        
        # Update tableau
        # Ensure op_tableau has correct size
        op_circuit = stim.Circuit()
        # Add Identity to force size
        # Or simpler: just use targets from 0 to 80?
        # But `I` gate is cheap.
        # Wait, stim checks for consistent qubit count.
        # op_circuit.append("I", [num_qubits-1]) might be enough if max index is num_qubits-1.
        op_circuit.append("I", [num_qubits - 1])
        op_circuit.append(op)
        
        op_tableau = stim.Tableau.from_circuit(op_circuit)
        
        # If op_tableau is still smaller (e.g. if num_qubits is larger than max index in op),
        # from_circuit should size it to max index used.
        # So we ensure max index used is num_qubits-1.
        
        current_tableau = current_tableau.then(op_tableau)

    print(f"Found {len(bad_faults)} bad faults.")
    
    with open("bad_faults.txt", "w") as f:
        for bf in bad_faults:
            f.write(str(bf) + "\n")
            
    bad_faults.sort(key=lambda x: x['weight'], reverse=True)
    
    seen = set()
    count = 0
    for bf in bad_faults:
        key = (bf['op_index'], bf['op_name'])
        if key not in seen:
            print(bf)
            seen.add(key)
            count += 1
            if count > 10: break

if __name__ == "__main__":
    analyze_faults("input.stim")
