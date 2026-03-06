import stim
import random
import copy
import sys

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
    
    # Baseline metrics
    best_cx = 210
    best_vol = 352
    
    print(f"Target: CX < {best_cx} OR (CX == {best_cx} AND Vol < {best_vol})")
    
    # Base tableau
    base_tableau = stim.Tableau.from_stabilizers(stabilizers, allow_redundant=True, allow_underconstrained=True)
    num_qubits = len(base_tableau)
    
    # Pre-compute gate tableaus
    try:
        gate_H = stim.Tableau.from_named_gate("H")
        gate_S = stim.Tableau.from_named_gate("S")
    except AttributeError:
        print("Error: stim.Tableau.from_named_gate not found.")
        sys.exit(1)
        
    found_better = False
    
    # Try 3000 iterations
    for k in range(3000):
        # Create a copy of the tableau
        current_tableau = base_tableau.copy()
        
        inverse_ops = []
        
        for q in range(num_qubits):
            choice = random.randint(0, 5)
            
            if choice == 0:
                pass
            elif choice == 1: # H
                current_tableau.prepend(gate_H, [q])
                inverse_ops.append(f"H {q}")
            elif choice == 2: # S
                current_tableau.prepend(gate_S, [q])
                inverse_ops.append(f"S_DAG {q}")
            elif choice == 3: # S H (Apply H then S)
                current_tableau.prepend(gate_H, [q])
                current_tableau.prepend(gate_S, [q])
                inverse_ops.append(f"H {q}")
                inverse_ops.append(f"S_DAG {q}")
            elif choice == 4: # H S (Apply S then H)
                current_tableau.prepend(gate_S, [q])
                current_tableau.prepend(gate_H, [q])
                inverse_ops.append(f"S_DAG {q}")
                inverse_ops.append(f"H {q}")
            elif choice == 5: # H S H
                current_tableau.prepend(gate_H, [q])
                current_tableau.prepend(gate_S, [q])
                current_tableau.prepend(gate_H, [q])
                inverse_ops.append(f"H {q}")
                inverse_ops.append(f"S_DAG {q}")
                inverse_ops.append(f"H {q}")
        
        # Synthesize
        try:
            synth_circuit = current_tableau.to_circuit("elimination")
            
            # Append inverse operations in REVERSE order
            suffix = stim.Circuit()
            for op in reversed(inverse_ops):
                suffix.append_from_stim_program_text(op)
            
            full_circuit = synth_circuit + suffix
            
            cx = count_cx(full_circuit)
            vol = count_volume(full_circuit)
            
            if cx < best_cx or (cx == best_cx and vol < best_vol):
                print(f"Iter {k}: Found BETTER! CX={cx}, Vol={vol}")
                best_cx = cx
                best_vol = vol
                found_better = True
                with open(r"C:\Users\anpaz\Repos\quantum-ai\rq3\data\agent_files\candidate.stim", "w") as f:
                    f.write(str(full_circuit))
            
            if k % 500 == 0:
                print(f"Iter {k}: Best CX={best_cx}, Vol={best_vol}")
                
        except Exception as e:
            pass

    if found_better:
        print("Finished search. Found improvement.")
    else:
        print("Finished search. No improvement found.")

if __name__ == "__main__":
    main()
