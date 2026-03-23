import stim
import sys

def load_circuit(path):
    with open(path, 'r') as f:
        content = f.read()
    return stim.Circuit(content)

def load_stabilizers(path):
    with open(path, 'r') as f:
        lines = f.readlines()
    return [line.strip() for line in lines if line.strip()]

def analyze_fault_propagation(circuit, data_qubits, distance):
    threshold = (distance - 1) // 2
    num_qubits = circuit.num_qubits
    
    # Flatten operations
    flat_ops = []
    for instruction in circuit:
        if isinstance(instruction, stim.CircuitRepeatBlock):
            pass
        else:
            name = instruction.name
            targets = instruction.targets_copy()
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

    bad_faults = []
    
    # T_rest represents the tableau of the circuit from the current point to the end.
    # Initially Identity (end of circuit).
    # We use num_qubits + extra margin just in case
    T_rest = stim.Tableau(num_qubits + 10) 
    
    # Reverse iterate
    ops_to_process = list(reversed(flat_ops))
    
    print(f"Analyzing {len(ops_to_process)} operations...")
    
    for i, (name, targets) in enumerate(ops_to_process):
        # Current point: effectively "after" the gate in forward time.
        
        # Check faults on the targets of this gate
        # (injecting fault after gate execution)
        
        current_gate_idx = len(ops_to_process) - 1 - i
        
        target_indices = []
        for t in targets:
            if t.is_qubit_target:
                target_indices.append(t.value)
        
        for qubit_idx in target_indices:
            for pauli in ['X', 'Z']: # focusing on X and Z faults usually sufficient for CSS? 
                                     # but let's check Y too if needed. 
                                     # For now X/Z is good first pass. Y=iXZ.
                
                # Propagate Pauli
                # applying T_rest to a Pauli string P gives T_rest P T_rest^{-1}.
                # This is "forward propagation" of the error P through the rest of the circuit.
                
                # Construct single-qubit Pauli
                ps = stim.PauliString(num_qubits + 10)
                if pauli == 'X': ps[qubit_idx] = 'X'
                elif pauli == 'Z': ps[qubit_idx] = 'Z'
                
                # Propagate
                propagated_ps = T_rest(ps)
                
                # Calculate weight on data qubits
                w = 0
                for dq in data_qubits:
                    # Check if index is within bounds
                    if dq < len(propagated_ps):
                        p_val = propagated_ps[dq]
                        if p_val != 0: # 0=I, 1=X, 2=Y, 3=Z
                            w += 1
                
                if w > threshold:
                    bad_faults.append(f"Gate {current_gate_idx} ({name} on {target_indices}): Fault {pauli} on {qubit_idx} spreads to {w} data qubits")

        # Update T_rest by PREPENDING the gate
        # T_rest_new = T_rest * Gate.
        # So we apply Gate then T_rest.
        # In stim: gate_tableau.then(T_rest)
        
        gate_circ = stim.Circuit()
        gate_circ.append(name, targets)
        gate_tableau = stim.Tableau.from_circuit(gate_circ)
        
        # Ensure tableau sizes match
        # If gate uses qubits beyond T_rest size, resize T_rest?
        # Creating larger tableau initially helps.
        
        T_rest = gate_tableau.then(T_rest)

    return bad_faults

if __name__ == "__main__":
    circuit = load_circuit(r"C:\Users\anpaz\Repos\quantum-ai\rq2\data\gemini-3-pro-preview\agent_files_ft\input.stim")
    # data qubits 0-104 based on stabilizer length
    data_qubits = list(range(105))
    
    print(f"Num data qubits: {len(data_qubits)}")
    print(f"Distance: 9, Threshold: 4")
    
    bad_faults = analyze_fault_propagation(circuit, data_qubits, 9)
    print(f"Found {len(bad_faults)} bad faults.")
    
    with open(r"C:\Users\anpaz\Repos\quantum-ai\rq2\data\gemini-3-pro-preview\agent_files_ft\bad_faults.txt", "w") as f:
        for fault in bad_faults:
            f.write(f"{fault}\n")
