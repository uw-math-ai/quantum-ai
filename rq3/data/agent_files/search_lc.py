import stim
import random

def count_cx(circuit):
    count = 0
    for instr in circuit:
        if instr.name == "CX" or instr.name == "CNOT":
            count += len(instr.targets_copy()) // 2
    return count

def count_volume(circuit):
    count = 0
    for instr in circuit:
        if instr.name in ["CX", "CNOT", "CY", "CZ", "H", "S", "S_DAG", "SQRT_X", "SQRT_X_DAG", "SQRT_Y", "SQRT_Y_DAG", "SQRT_Z", "SQRT_Z_DAG", "X", "Y", "Z", "I"]:
            if instr.name in ["CX", "CNOT", "CY", "CZ"]:
                count += len(instr.targets_copy()) // 2
            else:
                count += len(instr.targets_copy())
    return count

def get_stabilizers():
    with open(r"C:\Users\anpaz\Repos\quantum-ai\rq3\data\agent_files\stabilizers.txt", "r") as f:
        lines = f.readlines()
    return [stim.PauliString(line.strip()) for line in lines if line.strip()]

def main():
    stabilizers = get_stabilizers()
    
    # Baseline metrics (from previous run)
    best_cx = 210
    best_vol = 352
    
    print(f"Target: CX < {best_cx} OR (CX == {best_cx} AND Vol < {best_vol})")
    
    # Create a Tableau from stabilizers
    # We need a full tableau for conjugation? No, just stabilizers.
    # But stim methods work on Tableaus best.
    
    # Let's work with the tableau directly.
    # stim.Tableau.from_stabilizers creates a Tableau.
    # We can apply operations to it.
    
    tableau = stim.Tableau.from_stabilizers(stabilizers, allow_redundant=True, allow_underconstrained=True)
    num_qubits = len(tableau)
    
    found_better = False
    
    # Try 1000 iterations
    for k in range(1000):
        # Create a copy of the tableau
        current_tableau = tableau.copy()
        
        # Apply random local Cliffords
        # We will record the inverse operations to append later
        inverse_ops = []
        
        for q in range(num_qubits):
            # Pick a random Clifford from {I, H, S, SH, HS, HSH...}
            # Simplified: Randomly apply H, S some number of times
            # 0: I
            # 1: H
            # 2: S
            # 3: H S
            # 4: S H
            # 5: H S H
            choice = random.randint(0, 5)
            
            if choice == 0:
                pass
            elif choice == 1:
                current_tableau.prepend(stim.Circuit(f"H {q}"))
                inverse_ops.append(f"H {q}")
            elif choice == 2:
                current_tableau.prepend(stim.Circuit(f"S {q}"))
                inverse_ops.append(f"S_DAG {q}")
            elif choice == 3:
                current_tableau.prepend(stim.Circuit(f"S {q}"))
                current_tableau.prepend(stim.Circuit(f"H {q}"))
                inverse_ops.append(f"H {q}")
                inverse_ops.append(f"S_DAG {q}")
            elif choice == 4:
                current_tableau.prepend(stim.Circuit(f"H {q}"))
                current_tableau.prepend(stim.Circuit(f"S {q}"))
                inverse_ops.append(f"S_DAG {q}")
                inverse_ops.append(f"H {q}")
            elif choice == 5:
                current_tableau.prepend(stim.Circuit(f"H {q}"))
                current_tableau.prepend(stim.Circuit(f"S {q}"))
                current_tableau.prepend(stim.Circuit(f"H {q}"))
                inverse_ops.append(f"H {q}")
                inverse_ops.append(f"S_DAG {q}")
                inverse_ops.append(f"H {q}")
        
        # Synthesize
        try:
            synth_circuit = current_tableau.to_circuit("elimination")
            
            # Append inverse operations
            # inverse_ops list has ops for each qubit.
            # We applied T_new = U * T_old * U_dag? 
            # Wait. 
            # If we want to prepare State |S>, and we find U such that U|S> = |S'> (easier to synth).
            # Then |S> = U_dag |S'>.
            # So Circuit = U_dag * Circuit(S').
            # Here we applied gates to the tableau.
            # prepend(H) means the new tableau corresponds to the state AFTER H is applied?
            # No, prepend means we are modifying the tableau such that T_new = Op * T_old * Op_dag.
            # So T_new stabilizes U |psi>.
            # So we synthesize circuit for U |psi>.
            # Then we need to apply U_dag to get back to |psi>.
            # So Circuit_Total = U_dag + Circuit_Synth? No.
            # Circuit_Synth produces |psi'> = U |psi>.
            # We want |psi>. So we apply U_dag to |psi'>.
            # So Circuit = U_dag * Circuit_Synth? 
            # Yes, standard order is operations applied right to left in math, but left to right in circuit.
            # Circuit maps |0> to |psi'>.
            # Then apply U_dag: U_dag |psi'> = U_dag U |psi> = |psi>.
            # So append U_dag to the circuit.
            
            full_circuit = synth_circuit.copy()
            for op in inverse_ops[::-1]: # Reverse order of operations? 
                # inverse_ops were collected as we applied them.
                # If we applied H then S (HS), we need S_dag then H_dag (S_dag H_dag).
                # But my list has inverse ops stored.
                # If choice 3: applied H then S. stored H then S_dag.
                # Order in list: H, S_dag.
                # We need to append S_dag then H.
                # Wait.
                # Choice 3: prepend(S), prepend(H).
                # The tableau is T. T1 = S T S^dag. T2 = H T1 H^dag.
                # So T2 corresponds to state H S |psi>.
                # We want |psi> = S^dag H^dag |psi_2>.
                # So we append S^dag then H (H is self-inverse).
                # My `inverse_ops` stores: H, S_dag.
                # If I reverse it: S_dag, H.
                # Correct.
                pass
            
            # Actually just building a circuit string is easier
            suffix = stim.Circuit()
            for op in reversed(inverse_ops):
                suffix.append_from_stim_program_text(op)
            
            full_circuit += suffix
            
            cx = count_cx(full_circuit)
            vol = count_volume(full_circuit)
            
            if cx < best_cx or (cx == best_cx and vol < best_vol):
                print(f"Iter {k}: Found BETTER! CX={cx}, Vol={vol}")
                best_cx = cx
                best_vol = vol
                found_better = True
                with open(r"C:\Users\anpaz\Repos\quantum-ai\rq3\data\agent_files\candidate.stim", "w") as f:
                    f.write(str(full_circuit))
            
            if k % 100 == 0:
                print(f"Iter {k}: Best CX={best_cx}, Vol={best_vol}")
                
        except Exception as e:
            # print(e)
            pass

    if found_better:
        print("Finished search. Found improvement.")
    else:
        print("Finished search. No improvement found.")

if __name__ == "__main__":
    main()
