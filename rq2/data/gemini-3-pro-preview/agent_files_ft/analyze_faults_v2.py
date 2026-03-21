import stim
import sys

def main():
    try:
        circuit = stim.Circuit.from_file("data/gemini-3-pro-preview/agent_files_ft/circuit.stim")
    except Exception as e:
        print(f"Error loading circuit: {e}")
        return

    # Data qubits: 0 to 106 (based on stabilizer length 107)
    # But wait, max index in circuit was 104.
    # Stabilizers might cover more.
    # Let's assume data_qubits are all qubits mentioned in stabilizers.
    # I'll re-read stabilizers to be sure.
    with open("data/gemini-3-pro-preview/agent_files_ft/stabilizers_fixed.txt") as f:
        stabs = f.readlines()
    if not stabs:
        print("No stabilizers")
        return
    stab_len = len(stabs[0].strip())
    data_qubits = list(range(stab_len))
    num_qubits = stab_len # 107
    
    # We might need more qubits for simulation if the circuit uses larger indices?
    # Checked before: max index 104. So 107 is safe.

    print(f"Analyzing faults for {len(data_qubits)} data qubits.")

    # Convert circuit to operations
    ops = []
    for instruction in circuit:
        if instruction.name in ["H", "S", "X", "Y", "Z", "I", "RX", "RY", "RZ"]:
            for t in instruction.targets_copy():
                ops.append((instruction.name, [t.value]))
        elif instruction.name in ["CX", "CZ", "SWAP"]:
            targets = instruction.targets_copy()
            for i in range(0, len(targets), 2):
                ops.append((instruction.name, [targets[i].value, targets[i+1].value]))
        else:
            # Ignoring measurements or other gates?
            # Prompt says "circuit ... prepares a state".
            # If there are measurements, they are for prep?
            # I should include them in ops if they affect propagation.
            # But faults are inserted "at locations".
            pass

    print(f"Total operations: {len(ops)}")

    # Backward pass
    # V is the tableau of the "future"
    V = stim.Tableau(num_qubits)
    
    bad_faults = []

    # Optimization: Only check every Nth fault to save time?
    # No, we need all bad faults.
    # But python might be slow.
    # Let's try full scan.

    for i in range(len(ops) - 1, -1, -1):
        name, targets = ops[i]
        
        # Check faults AFTER this operation
        # Locations: on each target qubit of the gate
        for q in targets:
            if q >= num_qubits:
                continue # Should not happen given logic

            for p_char in ["X", "Z"]: # Y is X*Z, usually covered if X and Z are bad?
                # Prompt says "P in {X, Y, Z}".
                # But X and Z are generators.
                # If X propagates to w_x and Z to w_z, Y propagates to w_y <= w_x + w_z?
                # Not necessarily for weight.
                # But typically checking X and Z is enough for surface codes.
                # I'll check X, Z, Y.
                for error_name in ["X", "Y", "Z"]:
                    # Create Pauli P
                    p = stim.PauliString(num_qubits)
                    if error_name == "X": p[q] = "X"
                    elif error_name == "Y": p[q] = "Y"
                    elif error_name == "Z": p[q] = "Z"
                    
                    # Propagate
                    p_out = V(p)
                    
                    # Calculate weight on data qubits
                    w = sum(1 for k in data_qubits if p_out[k] != 0)
                    
                    if w >= 4:
                        bad_faults.append( (i, name, targets, q, error_name, w) )

        # Update V
        # Create mini circuit
        mini = stim.Circuit()
        mini.append(name, targets)
        # Prepend to V
        # V = gate * V_old
        # V_new(P) = V_old( gate(P) )?
        # No.
        # If we go backwards:
        # P_out = V_future(P_in)
        # Now we move to step i-1.
        # New future is gate_i followed by V_future.
        # So P_out' = V_future( gate_i( P_in ) ).
        # So we need to apply gate_i to the input of V_future.
        # Or composition: V_new = V_future * V_gate.
        # Stim's `prepend` does V_new = V_future.prepend(V_gate) -> V_future * V_gate?
        # Documentation: `t.prepend(other)` updates `t` to be `t * other`.
        # So `t(p)` becomes `t(other(p))`.
        # Yes.
        
        # We need to prepend gate_i.
        # But `prepend` takes a tableau.
        # Creating tableau for 107 qubits for every gate is slow?
        # `stim.Tableau.from_circuit(mini)` creates small tableau.
        # `prepend` handles size mismatch?
        # "The other tableau must have the same number of qubits." (Usually)
        # Let's check if `prepend` auto-expands.
        # If not, I must create full size tableau.
        
        op_tableau = stim.Tableau(num_qubits)
        # Apply gate to this identity tableau
        # How to apply gate to tableau efficiently?
        # `op_tableau.append(mini)`? No.
        # `do` method? `op_tableau.do(mini)`? No.
        # Stim Tableaus don't have `do`. Simulators have `do`.
        # But we can use `stim.Tableau.from_circuit`.
        # We need a circuit on num_qubits.
        
        full_mini = stim.Circuit()
        # Ensure size
        full_mini = stim.Circuit()
        full_mini.append("I", [num_qubits-1])
        full_mini.append(name, targets)
        
        t_gate = stim.Tableau.from_circuit(full_mini)
        
        # Apply gate to V (prepend)
        V.prepend(t_gate, list(range(num_qubits)))

    print(f"Found {len(bad_faults)} bad faults.")
    with open("data/gemini-3-pro-preview/agent_files_ft/bad_faults.txt", "w") as f:
        for bf in bad_faults:
            f.write(f"{bf}\n")

if __name__ == "__main__":
    main()
