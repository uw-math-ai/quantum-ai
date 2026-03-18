import stim

def analyze():
    with open('task_baseline.stim', 'r') as f:
        c = stim.Circuit(f.read())
    
    cx = c.num_2_qubit_gates()
    # Volume is total gates? No, the tool defines volume.
    # "volume – total gate count in the volume gate set (CX, CY, CZ, H, S, SQRT_X, etc.)"
    # Basically all gates except maybe Identity/Annotations?
    # Let's just count all operations for now as a proxy.
    vol = len(c) # This is instruction count, not gate count (since one instruction can have multiple targets)
    
    # Better volume count: sum of len(targets) for gate instructions?
    # The tool's definition of volume might be specific.
    # But usually minimizing total gate count is the goal.
    
    real_vol = 0
    real_cx = 0
    for op in c:
        if op.name in ["CX", "CNOT", "CZ", "CY"]:
             # Each pair is a gate
             real_cx += len(op.targets_copy()) // 2
             real_vol += len(op.targets_copy()) // 2
        elif op.name in ["H", "S", "X", "Y", "Z", "SQRT_X", "SQRT_Y", "SQRT_Z", "S_DAG", "SQRT_X_DAG", "SQRT_Y_DAG", "SQRT_Z_DAG"]:
             real_vol += len(op.targets_copy())
        
    print(f"Baseline CX: {real_cx}")
    print(f"Baseline Volume: {real_vol}")

if __name__ == "__main__":
    analyze()
