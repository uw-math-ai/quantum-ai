import stim
import random
import sys

def solve():
    # Load stabilizers
    with open("my_stabilizers.txt", "r") as f:
        stabilizers = [line.strip() for line in f if line.strip()]

    num_qubits = len(stabilizers[0])
    print(f"Num qubits: {num_qubits}")
    
    # Baseline metrics (from my_optimize.py)
    # Baseline: CX=270, Vol=295
    best_cx = 270
    best_vol = 295
    best_circuit = None
    
    # Convert to PauliString objects once
    pauli_stabs = [stim.PauliString(s) for s in stabilizers]
    
    # Try original first
    try:
        tableau = stim.Tableau.from_stabilizers(pauli_stabs, allow_underconstrained=True, allow_redundant=True)
        circ = tableau.to_circuit(method="elimination")
        
        cx = 0
        vol = 0
        for instr in circ:
            if instr.name == "CX" or instr.name == "CNOT":
                cx += len(instr.targets_copy()) // 2
                vol += len(instr.targets_copy()) // 2
            elif instr.name in ["H", "S", "S_DAG", "X", "Y", "Z", "I", "SQRT_X", "SQRT_X_DAG", "SQRT_Y", "SQRT_Y_DAG"]:
                 vol += len(instr.targets_copy())
        
        print(f"Original Elimination: CX={cx}, Vol={vol}")
        
        # We start with the baseline as the 'best' to beat
        # If elimination matches baseline, we keep it as a candidate if volume is better
        if cx < best_cx or (cx == best_cx and vol < best_vol):
             best_cx = cx
             best_vol = vol
             best_circuit = circ
             print("Original elimination is better than baseline!")

    except Exception as e:
        print(f"Error on original: {e}")

    # Search loop
    trials = 2000
    print(f"Starting search with {trials} trials...")
    
    indices = list(range(num_qubits))
    
    for t in range(trials):
        # Generate random permutation P
        random.shuffle(indices)
        P = indices[:] # P[physical] -> logical
        
        # P maps physical index i to logical index P[i]
        # To apply this to stabilizers, we need to know where the Pauli at physical i goes.
        # It goes to logical P[i].
        # So new_stab_string[P[i]] = old_stab_string[i].
        
        permuted_paulis = []
        try:
            for s_str in stabilizers:
                if len(s_str) != num_qubits:
                     # Skip or pad?
                     # Ideally all should be same length.
                     # If smaller, assume Identity on rest?
                     # But P[i] relies on i < num_qubits.
                     # If len(s_str) > num_qubits, we crash.
                     pass
                
                new_chars = ['I'] * num_qubits
                for i, char in enumerate(s_str):
                    if i < num_qubits:
                        new_chars[P[i]] = char
                permuted_paulis.append(stim.PauliString("".join(new_chars)))
        except Exception as e:
            print(f"Error permutation: {e}")
            continue
            
        try:
            tableau = stim.Tableau.from_stabilizers(permuted_paulis, allow_underconstrained=True, allow_redundant=True)
            circ = tableau.to_circuit(method="elimination")
            
            # Count metrics
            cx = 0
            vol = 0
            for instr in circ:
                if instr.name == "CX" or instr.name == "CNOT":
                    cx += len(instr.targets_copy()) // 2
                    vol += len(instr.targets_copy()) // 2
                elif instr.name in ["H", "S", "S_DAG", "X", "Y", "Z", "I", "SQRT_X", "SQRT_X_DAG", "SQRT_Y", "SQRT_Y_DAG"]:
                     vol += len(instr.targets_copy())
            
            if cx < best_cx or (cx == best_cx and vol < best_vol):
                print(f"Trial {t}: Found better! CX={cx}, Vol={vol}")
                best_cx = cx
                best_vol = vol
                
                # Un-permute the circuit
                # The circuit operations are on logical qubits.
                # Logical q corresponds to physical P_inv[q].
                # Where P_inv[P[i]] = i.
                
                P_inv = [0] * num_qubits
                for i, p in enumerate(P):
                    P_inv[p] = i
                    
                final_circ = stim.Circuit()
                for instr in circ:
                    # Map targets
                    new_targets = []
                    for t in instr.targets_copy():
                        if t.is_qubit_target:
                            new_val = P_inv[t.value]
                            new_targets.append(new_val)
                        elif t.is_x_target:
                            new_targets.append(stim.target_x(P_inv[t.value]))
                        elif t.is_y_target:
                            new_targets.append(stim.target_y(P_inv[t.value]))
                        elif t.is_z_target:
                            new_targets.append(stim.target_z(P_inv[t.value]))
                        else:
                             new_targets.append(t)
                    
                    final_circ.append(instr.name, new_targets, instr.gate_args_copy())
                
                best_circuit = final_circ
                
        except Exception as e:
            pass

    if best_circuit:
        with open("candidate.stim", "w") as f:
            f.write(str(best_circuit))
        print("Saved best candidate.")
    else:
        print("No improvement found.")

if __name__ == "__main__":
    solve()
