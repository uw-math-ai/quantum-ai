import stim
import sys

def load_circuit(path):
    with open(path, 'r') as f:
        content = f.read()
    return stim.Circuit(content)

def analyze_fault_propagation(circuit, data_qubits, distance):
    threshold = (distance - 1) // 2
    
    # Flatten operations
    flat_ops = []
    max_q = 0
    for instruction in circuit:
        if isinstance(instruction, stim.CircuitRepeatBlock):
            pass
        else:
            name = instruction.name
            targets = instruction.targets_copy()
            for t in targets:
                if t.is_qubit_target:
                    if t.value > max_q:
                        max_q = t.value
            
            # Decompose multi-target gates
            if name in ["CX", "CNOT", "CZ", "SWAP"]:
                # 2-qubit gates
                for i in range(0, len(targets), 2):
                    flat_ops.append((name, targets[i:i+2]))
            elif name in ["H", "S", "X", "Y", "Z", "I", "R", "M", "MR"]:
                # 1-qubit gates
                for t in targets:
                    flat_ops.append((name, [t]))
            else:
                 flat_ops.append((name, targets))

    # Ensure full size covers all qubits + margin
    full_size = max_q + 20
    
    bad_faults = []
    
    # T_rest represents the tableau of the circuit from the current point to the end.
    T_rest = stim.Tableau(full_size)
    
    ops_to_process = list(reversed(flat_ops))
    
    print(f"Analyzing {len(ops_to_process)} operations with full_size={full_size}...")
    
    for i, (name, targets) in enumerate(ops_to_process):
        current_gate_idx = len(ops_to_process) - 1 - i
        
        target_indices = []
        for t in targets:
            if t.is_qubit_target:
                target_indices.append(t.value)
        
        # Check faults
        for qubit_idx in target_indices:
            for pauli in ['X', 'Z']:
                # Propagate Pauli
                ps = stim.PauliString(full_size)
                if pauli == 'X': ps[qubit_idx] = 'X'
                elif pauli == 'Z': ps[qubit_idx] = 'Z'
                
                propagated_ps = T_rest(ps)
                
                w = 0
                for dq in data_qubits:
                    if dq < len(propagated_ps):
                        p_val = propagated_ps[dq]
                        if p_val != 0: 
                            w += 1
                
                if w > threshold:
                    bad_faults.append(f"Gate {current_gate_idx} ({name} on {target_indices}): Fault {pauli} on {qubit_idx} spreads to {w} data qubits")

        # Update T_rest
        # Construct tableau for this op OF FULL SIZE
        sim = stim.TableauSimulator()
        sim.do(stim.Circuit(f"I {full_size-1}")) # Force size
        
        gate_circ = stim.Circuit()
        gate_circ.append(name, targets)
        sim.do(gate_circ)
        
        t_op = sim.current_inverse_tableau().inverse()
        
        # T_rest = t_op.then(T_rest)
        # Check sizes
        if len(t_op) != len(T_rest):
            print(f"Size mismatch: t_op={len(t_op)}, T_rest={len(T_rest)}")
        
        T_rest = t_op.then(T_rest)

    return bad_faults

if __name__ == "__main__":
    circuit = load_circuit(r"C:\Users\anpaz\Repos\quantum-ai\rq2\data\gemini-3-pro-preview\agent_files_ft\input.stim")
    data_qubits = list(range(105)) # 0-104
    
    print(f"Num data qubits: {len(data_qubits)}")
    print(f"Distance: 9, Threshold: 4")
    
    bad_faults = analyze_fault_propagation(circuit, data_qubits, 9)
    print(f"Found {len(bad_faults)} bad faults.")
    
    with open(r"C:\Users\anpaz\Repos\quantum-ai\rq2\data\gemini-3-pro-preview\agent_files_ft\bad_faults.txt", "w") as f:
        for fault in bad_faults:
            f.write(f"{fault}\n")
