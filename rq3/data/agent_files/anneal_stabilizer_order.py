import stim
import random
import math
import copy

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

def evaluate(stab_order, stabilizers):
    # stab_order is a list of indices
    ordered_stabs = [stabilizers[i] for i in stab_order]
    try:
        tableau = stim.Tableau.from_stabilizers(ordered_stabs, allow_redundant=True, allow_underconstrained=True)
        synth_circuit = tableau.to_circuit("elimination")
        cx = count_cx(synth_circuit)
        vol = count_volume(synth_circuit)
        return cx, vol, synth_circuit
    except:
        return 9999, 9999, None

def main():
    stabilizers = get_stabilizers()
    num_stabs = len(stabilizers)
    
    best_cx = 210
    best_vol = 352
    
    print(f"Baseline: CX={best_cx}, Vol={best_vol}")
    
    current_order = list(range(num_stabs))
    current_cx, current_vol, _ = evaluate(current_order, stabilizers)
    
    best_order = list(current_order)
    best_overall_cx = best_cx
    best_overall_vol = best_vol
    
    T = 10.0
    alpha = 0.99
    
    iter_count = 0
    while iter_count < 2000:
        iter_count += 1
        
        # Propose move
        new_order = list(current_order)
        i, j = random.sample(range(num_stabs), 2)
        new_order[i], new_order[j] = new_order[j], new_order[i]
        
        cx, vol, circuit = evaluate(new_order, stabilizers)
        
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
            current_order = new_order
            current_cx = cx
            current_vol = vol
            
            # Check global best
            if cx < best_overall_cx or (cx == best_overall_cx and vol < best_overall_vol):
                print(f"Iter {iter_count}: Found BETTER! CX={cx}, Vol={vol}")
                best_overall_cx = cx
                best_overall_vol = vol
                best_order = list(new_order)
                with open(r"C:\Users\anpaz\Repos\quantum-ai\rq3\data\agent_files\candidate.stim", "w") as f:
                    f.write(str(circuit))
        
        T *= alpha
        if iter_count % 500 == 0:
            print(f"Iter {iter_count}: Temp={T:.4f}, Best CX={best_overall_cx}")

if __name__ == "__main__":
    main()
