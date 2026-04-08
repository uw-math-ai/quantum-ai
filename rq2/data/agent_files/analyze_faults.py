import stim

def get_weight(pauli_string, data_qubits):
    w = 0
    for q in data_qubits:
        if pauli_string[q] != 0: # 0=I, 1=X, 2=Y, 3=Z
            w += 1
    return w

def conjugate_pauli(p, gate_name, targets):
    # p is a stim.PauliString
    # We use stim's built-in conjugation if possible, or manual.
    # stim.PauliString.after(gate, targets) doesn't exist directly for arbitrary gates in this way.
    # But we can use a Tableau.
    
    # Actually, constructing a tableau for every gate is slow.
    # But N is small.
    # Let's use stim.Tableau.from_circuit for the single gate operation.
    
    # Create a mini circuit for this gate
    mini_circ = stim.Circuit()
    mini_circ.append(gate_name, targets)
    
    # Get the tableau. 
    # Wait, pushing P through U is P' = U P U^dag.
    # In Stim, tableau T represents U^dag (inverse).
    # T(P) = U^dag P U. 
    # We want U P U^dag = (U^dag)^dag P U^dag.
    # So we want T.inverse()(P).
    # But wait, Stim's tableau application `t(p)` computes `t * p * t.inverse()`.
    # Let's verify.
    # If T corresponds to Clifford C, T(P) gives the Pauli P' such that P' = C P C^dag.
    # Yes, Stim Tableaus act as Heisenberg conjugation maps.
    # So if we have gate G, we want P' = G P G^dag.
    # We just need the Tableau for G, say T_G. Then P' = T_G(P).
    
    T_G = stim.Tableau.from_circuit(mini_circ)
    return T_G(p)

def main():
    circuit = stim.Circuit.from_file("circuit_input.stim")
    
    # Flatten into primitive operations
    ops = []
    for instruction in circuit:
        if instruction.name in ["H", "S"]:
            for t in instruction.targets_copy():
                ops.append((instruction.name, [t.value]))
        elif instruction.name == "CX":
            targets = instruction.targets_copy()
            for i in range(0, len(targets), 2):
                ops.append(("CX", [targets[i].value, targets[i+1].value]))
        else:
            print(f"Unknown gate {instruction.name}")
            return

    # Data qubits are 0 to 34
    data_qubits = list(range(35))
    num_qubits = 35 # Sufficiently large. 
    # Actually circuit uses up to 34. So 35 is fine.
    
    bad_faults = []

    print(f"Total primitive ops: {len(ops)}")
    
    # Backward pass
    # V represents the unitary of the "future" circuit
    V = stim.Tableau(num_qubits)
    
    # Iterate backwards
    for i in range(len(ops) - 1, -1, -1):
        gate_name, targets = ops[i]
        
        # Check faults AFTER this gate (propagated by current V)
        for q in targets:
            for error_name in ["X", "Y", "Z"]:
                # Create Pauli string P
                # We can't easily create a full PauliString and pass to V if V is smaller?
                # V is size 35. P must be size 35.
                p = stim.PauliString(num_qubits)
                
                # Check if q is within bounds
                if q >= num_qubits:
                     # Resize V if needed? 
                     # But we know q <= 34.
                     pass
                
                if error_name == "X":
                    p[q] = "X"
                elif error_name == "Z":
                    p[q] = "Z"
                elif error_name == "Y":
                    p[q] = "Y"
                
                # Propagate P through V
                p_out = V(p)
                
                w = get_weight(p_out, data_qubits)
                if w >= 4:
                    # Report
                    # print(f"Fault at op {i} ({gate_name} {targets}) on qubit {q} type {error_name} -> weight {w}")
                    bad_faults.append((i, gate_name, targets, q, error_name, w))
        
        # Update V by prepending this gate
        # Create mini circuit for this gate
        mini_circ = stim.Circuit()
        mini_circ.append(gate_name, targets)
        t_op = stim.Tableau.from_circuit(mini_circ)
        
        # Determine max qubit index in this op to ensure size compatibility
        # t_op will have size max(targets)+1.
        # V has size 35.
        # If t_op is smaller, it's fine?
        # stim.Tableau.prepend requires same size?
        # Let's check.
        # Usually it expands if needed or assumes identity on missing qubits.
        # But safest is to pad t_op to 35.
        
        # Actually, t_op = stim.Tableau(35)
        # Then apply gate to it? 
        # No, tableau from circuit gives minimal size.
        # We can create a full size circuit.
        
        mini_circ_full = stim.Circuit()
        # To force size 35, add an Identity on qubit 34 if needed?
        # Or just append I 34.
        mini_circ_full.append("I", [num_qubits-1]) 
        mini_circ_full.append(gate_name, targets)
        t_op = stim.Tableau.from_circuit(mini_circ_full)
        
        V.prepend(t_op, list(range(num_qubits)))

    print(f"Found {len(bad_faults)} bad faults.")
    
    # Save to file
    with open("bad_faults.txt", "w") as f:
        for fault in bad_faults:
            f.write(f"{fault}\n")

if __name__ == "__main__":
    main()
