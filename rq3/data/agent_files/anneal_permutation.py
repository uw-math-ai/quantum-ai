import stim
import random
import math
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

def map_stabilizers(stabilizers, perm):
    # perm[i] is the new index for qubit i
    # We want to map PauliString such that P'_new = P_old
    mapped_stabilizers = []
    num_qubits = 30
    
    for s in stabilizers:
        s_str = str(s)
        sign_char = ""
        if s_str.startswith("+"):
            s_str = s_str[1:]
            sign_char = "+"
        elif s_str.startswith("-"):
            s_str = s_str[1:]
            sign_char = "-"
        else:
            sign_char = "+"
            
        if len(s_str) < num_qubits:
             s_str = s_str + "_" * (num_qubits - len(s_str))
             
        new_chars = ["_"] * num_qubits
        for i, char in enumerate(s_str):
            if i < num_qubits:
                new_chars[perm[i]] = char
        
        new_s_str = sign_char + "".join(new_chars)
        mapped_stabilizers.append(stim.PauliString(new_s_str))
        
    return mapped_stabilizers

def unmap_circuit(circuit, perm):
    # perm maps old_index -> new_index
    # circuit uses new_index
    # we want to map back to old_index
    # inv_perm[new_index] = old_index
    
    inv_perm = [0] * len(perm)
    for old, new in enumerate(perm):
        inv_perm[new] = old
        
    new_circuit = stim.Circuit()
    for instr in circuit:
        if instr.name in ["CX", "CNOT", "CY", "CZ", "H", "S", "S_DAG", "SQRT_X", "SQRT_X_DAG", "SQRT_Y", "SQRT_Y_DAG", "SQRT_Z", "SQRT_Z_DAG", "X", "Y", "Z", "I", "M", "R"]:
            targets = instr.targets_copy()
            new_targets = []
            for t in targets:
                if t.is_qubit_target:
                    new_targets.append(stim.target_rec(inv_perm[t.value]))
                else:
                    new_targets.append(t)
            new_circuit.append(instr.name, new_targets, instr.gate_args_copy())
        else:
            new_circuit.append(instr)
            
    return new_circuit

def evaluate(perm, stabilizers):
    mapped_stabs = map_stabilizers(stabilizers, perm)
    try:
        tableau = stim.Tableau.from_stabilizers(mapped_stabs, allow_redundant=True, allow_underconstrained=True)
        synth_circuit = tableau.to_circuit("elimination")
        final_circuit = unmap_circuit(synth_circuit, perm)
        cx = count_cx(final_circuit)
        vol = count_volume(final_circuit)
        return cx, vol, final_circuit
    except:
        return 9999, 9999, None

def main():
    stabilizers = get_stabilizers()
    
    best_cx = 210
    best_vol = 352
    
    print(f"Baseline: CX={best_cx}, Vol={best_vol}")
    
    current_perm = list(range(30))
    current_cx, current_vol, _ = evaluate(current_perm, stabilizers)
    
    best_perm = list(current_perm)
    best_overall_cx = best_cx
    best_overall_vol = best_vol
    
    T = 10.0
    alpha = 0.99
    
    iter_count = 0
    while iter_count < 1000:
        iter_count += 1
        
        # Propose move
        new_perm = list(current_perm)
        i, j = random.sample(range(30), 2)
        new_perm[i], new_perm[j] = new_perm[j], new_perm[i]
        
        cx, vol, circuit = evaluate(new_perm, stabilizers)
        
        # Energy = cx + vol * 0.001 (prioritize cx)
        current_energy = current_cx + current_vol * 0.0001
        new_energy = cx + vol * 0.0001
        
        delta = new_energy - current_energy
        
        accept = False
        if delta < 0:
            accept = True
        else:
            if random.random() < math.exp(-delta / T):
                accept = True
                
        if accept:
            current_perm = new_perm
            current_cx = cx
            current_vol = vol
            
            # Check global best
            if cx < best_overall_cx or (cx == best_overall_cx and vol < best_overall_vol):
                print(f"Iter {iter_count}: Found BETTER! CX={cx}, Vol={vol}")
                best_overall_cx = cx
                best_overall_vol = vol
                best_perm = list(new_perm)
                with open(r"C:\Users\anpaz\Repos\quantum-ai\rq3\data\agent_files\candidate.stim", "w") as f:
                    f.write(str(circuit))
        
        T *= alpha
        if iter_count % 100 == 0:
            print(f"Iter {iter_count}: Temp={T:.4f}, Best CX={best_overall_cx}")

if __name__ == "__main__":
    main()
