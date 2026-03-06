import stim

def optimize():
    c = stim.Circuit.from_file("baseline_task_v10.stim")
    print(f"Original instructions: {len(c)}")
    ops = list(c)
    
    # 1. Cancel adjacent self-inverses
    optimized = []
    skipped = 0
    for op in ops:
        skip = False
        if len(optimized) > 0:
            last = optimized[-1]
            if str(last) == str(op) and op.name in ["H", "CX", "CZ", "X", "Y", "Z"]:
                optimized.pop()
                skipped += 1
                skip = True
        
        if not skip:
            optimized.append(op)
        
    print(f"Cancelled {skipped} pairs")
    
    out = stim.Circuit()
    for op in optimized:
        out.append(op)
        
    with open("candidate_opt.stim", "w") as f:
        f.write(str(out))
    
    cx_old = 0
    for op in ops:
        if op.name == "CX": cx_old += 1
    
    cx_new = 0
    for op in optimized:
        if op.name == "CX": cx_new += 1
        
    print(f"CX count: {cx_old} -> {cx_new}")

if __name__ == "__main__":
    optimize()
