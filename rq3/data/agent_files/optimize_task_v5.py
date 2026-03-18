import stim
import sys

def count_cx(circuit):
    count = 0
    for instruction in circuit:
        if instruction.name == "CX" or instruction.name == "CNOT":
            # targets_copy() returns a list of targets
            count += len(instruction.targets_copy()) // 2
    return count

def get_volume(circuit):
    # simple volume count: total number of operations
    # But the prompt says: "total gate count in the volume gate set (CX, CY, CZ, H, S, SQRT_X, etc.)"
    # This implies 1-qubit and 2-qubit gates count.
    count = 0
    gate_set = ["CX", "CNOT", "CY", "CZ", "H", "S", "S_DAG", "SQRT_X", "SQRT_X_DAG", "SQRT_Y", "SQRT_Y_DAG", "SQRT_Z", "SQRT_Z_DAG", "X", "Y", "Z", "I"]
    for instruction in circuit:
        if instruction.name in gate_set:
            targets = instruction.targets_copy()
            if instruction.name in ["CX", "CNOT", "CY", "CZ"]:
                 count += len(targets) // 2
            else:
                 count += len(targets)
    return count

def read_stabilizers(path):
    with open(path, 'r') as f:
        lines = [line.strip() for line in f if line.strip()]
    return lines

def main():
    stabilizers = read_stabilizers("stabilizers_task_v2.txt")
    baseline = stim.Circuit.from_file("baseline_task_v2.stim")
    
    print(f"Baseline CX: {count_cx(baseline)}")
    print(f"Baseline Volume: {get_volume(baseline)}")
    
    # Attempt 1: Direct synthesis from stabilizers
    # stim.Tableau.from_stabilizers expects a list of PauliStrings.
    # The input format is strings like "XZ...", so we need to parse them.
    # But wait, from_stabilizers takes a list of stim.PauliString.
    
    stab_objs = []
    for s in stabilizers:
        # Stabilizer strings might have extra spaces or newlines
        s = s.strip()
        if not s: continue
        stab_objs.append(stim.PauliString(s))
        
    try:
        # Method 1: Elimination
        tableau = stim.Tableau.from_stabilizers(stab_objs, allow_underconstrained=True)
        circuit1 = tableau.to_circuit("elimination")
        
        c1_cx = count_cx(circuit1)
        c1_vol = get_volume(circuit1)
        print(f"Method 'elimination' CX: {c1_cx}, Volume: {c1_vol}")
        
        with open("candidate_elimination.stim", "w") as f:
            f.write(str(circuit1))
            
        # Method 2: Graph State
        circuit2 = tableau.to_circuit("graph_state")
        
        c2_cx = count_cx(circuit2)
        c2_vol = get_volume(circuit2)
        print(f"Method 'graph_state' CX: {c2_cx}, Volume: {c2_vol}")
        
        with open("candidate_graph_state.stim", "w") as f:
            f.write(str(circuit2))

    except Exception as e:
        print(f"Synthesis failed: {e}")

if __name__ == "__main__":
    main()
