import stim
import sys

def generate_circuit():
    with open("input.stim", "r") as f:
        circuit_str = f.read()
    circuit = stim.Circuit(circuit_str)
    num_qubits = max(circuit.num_qubits, 81)
    ops = list(circuit)
    
    with open("stabilizers.txt", "r") as f:
        stabs_str = [line.strip() for line in f if line.strip()]
    stabilizers = [stim.PauliString(s) for s in stabs_str]
    
    # Recompute stabs_map
    stabs_map = {}
    curr = [s for s in stabilizers]
    stabs_map[len(ops)] = curr
    
    # We need to use the exact same logic as analyze_coverage to ensure indices match
    for i in range(len(ops) - 1, -1, -1):
        op = ops[i]
        op_circuit = stim.Circuit()
        op_circuit.append("I", [num_qubits - 1])
        op_circuit.append(op)
        op_tableau = stim.Tableau.from_circuit(op_circuit)
        
        next_s = []
        for s in curr:
            next_s.append(op_tableau(s))
        curr = next_s
        stabs_map[i] = curr

    # Read checks
    checks = {}
    with open("checks.txt", "r") as f:
        for line in f:
            if not line.strip(): continue
            parts = line.strip().split(":")
            step = int(parts[0])
            indices = [int(x) for x in parts[1].split(",")]
            checks[step] = indices
            
    # Build new circuit
    new_circuit = stim.Circuit()
    
    # Ancilla allocation
    next_ancilla = 81
    flag_qubits = []
    
    # Initial H for all flags?
    # No, we add them as needed.
    # But flags must be measured at end.
    # So we init them at the start or when used?
    # "All ancilla qubits must be initialized in the |0> state and measured at the end"
    # So we can init them when used, but must measure at end.
    
    for i in range(len(ops)):
        # Insert checks BEFORE op i? 
        # In analyze_coverage: "record that we need to measure stabilizer best_s_idx at step i+1"
        # This was for faults AFTER op i.
        # So check should be AFTER op i.
        
        new_circuit.append(ops[i])
        
        step = i + 1
        if step in checks:
            s_indices = checks[step]
            current_stabs = stabs_map[step]
            
            for s_idx in s_indices:
                s = current_stabs[s_idx]
                
                flag = next_ancilla
                next_ancilla += 1
                flag_qubits.append(flag)
                
                # Gadget for measuring stabilizer s
                # Init |0> is implied (new qubit)
                # But to be safe/explicit, we can R 0? 
                # Stim assumes 0 for new qubits?
                # Usually yes. But let's add R just in case?
                # "All ancilla qubits must be initialized in the |0> state"
                # If we reuse ancillas, we need R.
                # If we use fresh, they are 0.
                # I'll use fresh.
                
                # H flag
                new_circuit.append("H", [flag])
                
                # Controlled Paulis
                # s is PauliString.
                # Iterate over qubits in s
                # We need the qubits indices where s is not I.
                # s has length 81.
                
                # We can iterate 0 to 80.
                s_str = str(s)
                # format "+_XZ..."
                
                for q in range(81):
                    # char at q+1
                    if q+1 >= len(s_str): break
                    char = s_str[q+1]
                    
                    if char == 'X':
                        new_circuit.append("CX", [flag, q])
                    elif char == 'Z':
                        new_circuit.append("CZ", [flag, q])
                    elif char == 'Y':
                        # Handle Y if present
                        # S_dag CX S
                        # S_dag on q, CX flag->q, S on q
                        new_circuit.append("S_DAG", [q])
                        new_circuit.append("CX", [flag, q])
                        new_circuit.append("S", [q])
                        
                # H flag
                new_circuit.append("H", [flag])
                
                # We don't measure yet. Measure at end.

    # Measure all flags at end
    if flag_qubits:
        new_circuit.append("M", flag_qubits)
        
    # Output
    print(new_circuit)
    
    # Write to file for validation
    with open("candidate.stim", "w") as f:
        f.write(str(new_circuit))
        
    # Write return args
    with open("return_args.txt", "w") as f:
        f.write(f"{flag_qubits}")

if __name__ == "__main__":
    generate_circuit()
