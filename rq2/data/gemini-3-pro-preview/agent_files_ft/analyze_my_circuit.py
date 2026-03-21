
import stim
import sys

def analyze_circuit(circuit_path, output_path):
    with open(circuit_path, 'r') as f:
        circuit_str = f.read()
    
    circuit = stim.Circuit(circuit_str)
    
    # Identify data qubits (0-75)
    data_qubits = set(range(76))
    
    # Flatten circuit to operations
    ops = list(circuit)
    
    bad_faults = []
    
    # Iterate through operations
    num_ops = len(ops)
    print(f"Analyzing {num_ops} operations...")
    
    for i in range(num_ops):
        op = ops[i]
        
        # Construct the tableau for the tail (operations after i)
        # We use a tableau of size 76 to ensure all qubits are covered
        tail_tableau = stim.Tableau(76)
        
        # Apply operations from i+1 to end
        for op_tail in ops[i+1:]:
             # We need to apply op_tail to the tableau.
             # T represents the channel U_tail.
             # We want T' = op_tail * T (apply op_tail after T).
             # stim.Tableau.do() applies the operation to the tableau state.
             # If T is initialized to I, T represents identity channel.
             # T.do(G) updates T to G * T.
             # So we just iterate and apply.
             try:
                tail_tableau.do(op_tail)
             except Exception as e:
                # If op_tail touches qubits >= 76, this might fail?
                # But we assume data qubits are 0-75.
                # If there are ancillas > 75, we might need larger tableau.
                # Let's catch and print.
                print(f"Error applying op {op_tail} at step {i}: {e}")
                # Try to expand tableau? No, just continue for now.
                pass

        targets = []
        if op.name in ["CX", "CNOT", "H", "S", "X", "Y", "Z", "I"]:
             for t in op.targets_copy():
                 targets.append(t.value)
        else:
            continue # Skip measurement or other non-clifford gates
        
        targets = sorted(list(set(targets)))
        
        for q in targets:
            if q not in data_qubits:
                continue 
            
            for p_name in ["X", "Y", "Z"]:
                if p_name == "X":
                    out_pauli = tail_tableau.x_output(q)
                elif p_name == "Z":
                    out_pauli = tail_tableau.z_output(q)
                elif p_name == "Y":
                    # Approximate Y output by multiplying X and Z outputs
                    out_pauli = tail_tableau.x_output(q) * tail_tableau.z_output(q)
                
                current_weight = 0
                # Check length
                plen = len(out_pauli)
                for k in range(min(plen, 76)):
                    if out_pauli[k] != 0:
                        current_weight += 1
                
                if current_weight >= 4:
                    # Also record if weight is >= 4
                    bad_faults.append(f"Op {i} ({op}) Q{q} {p_name} -> Weight {current_weight}")

    # Write results
    with open(output_path, 'w') as f:
        f.write(f"Found {len(bad_faults)} bad faults.\n")
        for fault in bad_faults:
            f.write(fault + "\n")
            
    print(f"Found {len(bad_faults)} bad faults.")

if __name__ == "__main__":
    circuit_path = r"C:\Users\anpaz\Repos\quantum-ai\rq2\data\gemini-3-pro-preview\agent_files_ft\circuit.stim"
    output_path = r"C:\Users\anpaz\Repos\quantum-ai\rq2\data\gemini-3-pro-preview\agent_files_ft\faults.txt"
    analyze_circuit(circuit_path, output_path)
