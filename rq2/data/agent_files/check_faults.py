import stim
import sys

def check_stabilizers(circuit, stabilizers):
    # Check if circuit preserves stabilizers
    # S |psi> = |psi>
    # U^dag S U |0> = |0>
    
    sim = stim.TableauSimulator()
    sim.do(circuit)
    
    # We can use the simulator to peek at observables
    # But simpler is to use the tableau method
    t = stim.Tableau.from_circuit(circuit)
    
    preserved = 0
    total = len(stabilizers)
    
    for s_str in stabilizers:
        s = stim.PauliString(s_str)
        # Compute U^dag S U
        # t(P) computes U^dag P U
        p = t(s)
        
        p_str = str(p)
        failed = False
        if "X" in p_str or "Y" in p_str:
            failed = True
        if p_str.startswith("-"):
            failed = True
            
        if failed:
            if preserved < 5: # Print first 5 failures
                print(f"Failed stabilizer: {s_str}")
                print(f"Mapped to: {p_str}")
        else:
            preserved += 1
        
    return preserved, total

def get_weight(pauli_string, data_qubits_set):
    w = 0
    # efficient iteration?
    # pauli_string is iterable, yields 0,1,2,3
    # data_qubits is 0..174
    # The string might be longer if we have ancillas.
    # We only care about data qubits.
    
    # Using the string representation might be slow for inner loop
    # access by index is better
    for q in data_qubits_set:
        if pauli_string[q] != 0:
            w += 1
    return w

def main():
    with open("circuit_input.stim", "r") as f:
        circuit_str = f.read()
    circuit = stim.Circuit(circuit_str)
    
    with open("stabilizers.txt", "r") as f:
        stabilizers = [line.strip() for line in f if line.strip()]
    
    for i in range(len(stabilizers)):
        s = stabilizers[i]
        if len(s) < 175:
            stabilizers[i] = s + "I" * (175 - len(s))
        elif len(s) > 175:
            stabilizers[i] = s[:175]
            
    stab_len = 175
    circ_qubits = circuit.num_qubits
    print(f"Stabilizer length: {stab_len}")
    print(f"Circuit num_qubits: {circ_qubits}")
    
    num_qubits = max(stab_len, circ_qubits)
    
    # Pad circuit if needed
    if circ_qubits < num_qubits:
        circuit.append("I", [num_qubits - 1])
        
    print(f"Checking stabilizers ({len(stabilizers)})...")
    preserved, total = check_stabilizers(circuit, stabilizers)
    print(f"Stabilizers preserved: {preserved}/{total}")
    
    if preserved < total:
        print("WARNING: Not all stabilizers are preserved by the baseline!")
        
    print("Checking faults...")
    
    # Flatten ops
    ops = []
    for instruction in circuit:
        if instruction.name in ["H", "S", "I", "X", "Y", "Z"]:
            for t in instruction.targets_copy():
                ops.append((instruction.name, [t.value]))
        elif instruction.name == "CX":
            targets = instruction.targets_copy()
            for i in range(0, len(targets), 2):
                ops.append(("CX", [targets[i].value, targets[i+1].value]))
        # Add other gates if present? 
        # The input circuit only has H and CX.
        
    # Propagator W, starts as Identity
    # We need a tableau of size num_qubits
    # If we add ancillas later, we need to handle that.
    # For now, baseline uses 175.
    W = stim.Tableau(num_qubits)
    
    data_qubits_set = set(range(175))
    bad_faults = []
    
    # Backward pass
    for i in range(len(ops) - 1, -1, -1):
        name, targets = ops[i]
        
        # Check faults injected AFTER this gate (and before next gates)
        # For each target qubit of the gate, inject X, Y, Z
        # Actually, faults can happen on any qubit at any time.
        # But usually we model faults at gate locations.
        # The prompt says: "A fault is a location in the circuit where there is an unexpected disruption ... C[l <- P]"
        # "l in spots(C)". Spots usually means gate locations.
        # So we inject errors on the qubits involved in the gate.
        
        for q in targets:
            for error_type in ["X", "Y", "Z"]:
                # Create error P
                p = stim.PauliString(num_qubits)
                if error_type == "X": p[q] = "X"
                elif error_type == "Y": p[q] = "Y"
                elif error_type == "Z": p[q] = "Z"
                
                # Propagate forward using W
                p_out = W(p)
                
                w = get_weight(p_out, data_qubits_set)
                
                # Threshold is 7. If w >= 7, must flag.
                if w >= 7:
                    # Check if flagged (no flags yet)
                    flagged = False
                    if not flagged:
                        bad_faults.append(f"Op {i} {name} {targets} qubit {q} {error_type} -> weight {w}")
        
        # Update W by prepending G_inv
        # G_inv for H is H. For CX is CX.
        # Construct tableau for G_inv
        mini = stim.Circuit()
        mini.append(name, targets) # Self-inverse for H and CX
        t_inv = stim.Tableau.from_circuit(mini)
        
        # We need to make sure t_inv acts on the full set of qubits or compatible
        # stim.Tableau.from_circuit creates a tableau of size sufficient for targets.
        # W is size num_qubits.
        # We can expand t_inv?
        # Or simpler: create a full circuit for t_inv
        full_mini = stim.Circuit()
        full_mini.append("I", [num_qubits-1]) # Force size
        full_mini.append(name, targets)
        t_inv = stim.Tableau.from_circuit(full_mini)
        
        # W = t_inv.then(W) => W.prepend(t_inv)
        W.prepend(t_inv)
        
    print(f"Found {len(bad_faults)} bad faults.")
    with open("bad_faults.txt", "w") as f:
        for bf in bad_faults:
            f.write(bf + "\n")
            
if __name__ == "__main__":
    main()
