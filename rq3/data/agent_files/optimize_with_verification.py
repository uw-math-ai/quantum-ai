import stim
import random
import time
import sys

def count_cx(circuit):
    count = 0
    for instr in circuit:
        if instr.name == "CX" or instr.name == "CNOT":
            count += len(instr.targets_copy()) // 2
    return count

def compute_volume(circuit):
    count = 0
    for instr in circuit:
        if instr.name in ["CX", "CNOT", "CY", "CZ", "H", "S", "S_DAG", "SQRT_X", "SQRT_X_DAG", "SQRT_Y", "SQRT_Y_DAG", "SQRT_Z", "SQRT_Z_DAG", "X", "Y", "Z", "I", "SWAP", "ISWAP"]:
            if instr.name in ["CX", "CNOT", "CY", "CZ", "SWAP", "ISWAP"]:
                count += len(instr.targets_copy()) // 2
            else:
                count += len(instr.targets_copy())
    return count

def apply_permutation(stabilizers, permutation):
    num_qubits = len(permutation)
    new_stabilizers = []
    for s in stabilizers:
        chars = ['I'] * num_qubits
        for i, char in enumerate(s):
            if i < num_qubits:
                chars[permutation[i]] = char
        new_stabilizers.append("".join(chars))
    return new_stabilizers

def inverse_permutation(perm):
    inv = [0] * len(perm)
    for i, p in enumerate(perm):
        inv[p] = i
    return inv

def relabel_circuit(circuit, mapping):
    new_circuit = stim.Circuit()
    for instr in circuit:
        targets = []
        for t in instr.targets_copy():
            if t.is_qubit_target:
                targets.append(mapping[t.value])
            elif t.is_x_target:
                targets.append(stim.target_x(mapping[t.value]))
            elif t.is_y_target:
                targets.append(stim.target_y(mapping[t.value]))
            elif t.is_z_target:
                targets.append(stim.target_z(mapping[t.value]))
            elif t.is_combiner:
                targets.append(stim.target_combiner())
            else:
                targets.append(t) 
        new_circuit.append(instr.name, targets, instr.gate_args_copy())
    return new_circuit

def check_preservation(circuit, stabilizers):
    sim = stim.TableauSimulator()
    sim.do(circuit)
    preserved = 0
    for s_str in stabilizers:
        s = stim.PauliString(s_str)
        if sim.peek_observable_expectation(s) == 1:
            preserved += 1
    return preserved

def main():
    try:
        with open("stabilizers_task.txt", "r") as f:
            stabilizers = [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        print("stabilizers_task.txt not found")
        return

    num_qubits = len(stabilizers[0])
    print(f"Num qubits: {num_qubits}")

    # Baseline metrics (approximate, we want better than 839)
    base_cx = 839 
    base_vol = 888
    
    best_cx = base_cx
    best_vol = base_vol
    best_circuit = None
    
    start_time = time.time()
    attempts = 0
    
    # Try identity first (permutation 0)
    # Then random
    
    while time.time() - start_time < 90:
        attempts += 1
        current_perm = list(range(num_qubits))
        if attempts > 1:
            random.shuffle(current_perm)
            
        permuted_stabilizers_str = apply_permutation(stabilizers, current_perm)
        permuted_stabilizers = [stim.PauliString(s) for s in permuted_stabilizers_str]
        
        try:
            tableau = stim.Tableau.from_stabilizers(permuted_stabilizers, allow_underconstrained=True)
            circuit = tableau.to_circuit(method="elimination")
            
            # Relabel immediately to check metrics and validity
            inv_perm = inverse_permutation(current_perm)
            candidate = relabel_circuit(circuit, inv_perm)
            
            cx = count_cx(candidate)
            vol = compute_volume(candidate)
            
            # Optimization check
            is_better = (cx < best_cx) or (cx == best_cx and vol < best_vol)
            
            if is_better:
                # Verify immediately
                preserved = check_preservation(candidate, stabilizers)
                if preserved == len(stabilizers):
                    print(f"Found better VALID! CX: {cx}, Vol: {vol} (Attempt {attempts})")
                    best_cx = cx
                    best_vol = vol
                    best_circuit = candidate
                    
                    with open("best_candidate.stim", "w") as f:
                        f.write(str(best_circuit))
                else:
                    print(f"Found better ({cx}) but INVALID ({preserved}/{len(stabilizers)} preserved). Ignoring.")
            
            if attempts % 10 == 0:
                print(f"Attempt {attempts}: Best CX={best_cx}, Vol={best_vol}")
                
        except Exception as e:
            print(f"Error in attempt {attempts}: {e}")
            continue

    print(f"\nFinished {attempts} attempts.")
    if best_circuit:
        print("Optimization successful.")
    else:
        print("No improvement found.")

if __name__ == "__main__":
    main()
