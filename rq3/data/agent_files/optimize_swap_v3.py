import stim

def count_metrics(circuit):
    cx = 0
    vol = 0
    for instr in circuit:
        if instr.name in ["CX", "CNOT"]:
            count = len(instr.targets_copy()) // 2
            cx += count
            vol += count
        elif instr.name in ["CX", "CY", "CZ", "SWAP", "H", "S", "SQRT_X", "SQRT_Y", "SQRT_Z", "X", "Y", "Z", "I"]:
            if instr.name in ["CX", "CY", "CZ", "SWAP"]:
                 count = len(instr.targets_copy()) // 2
                 vol += count
            else: 
                 count = len(instr.targets_copy())
                 vol += count
    return cx, vol

def check_preservation(circuit, stabs):
    sim = stim.TableauSimulator()
    sim.do(circuit)
    preserved = 0
    for stab in stabs:
        p = stim.PauliString(stab)
        if sim.peek_observable_expectation(p) == 1:
            preserved += 1
    return preserved

def optimize():
    # Load baseline
    with open("baseline.stim", "r") as f:
        baseline_text = f.read()
    c = stim.Circuit(baseline_text)
    
    base_cx, base_vol = count_metrics(c)
    print(f"Baseline Metrics: CX={base_cx}, Vol={base_vol}")
    
    # Load Stabilizers
    with open("target_stabilizers.txt", "r") as f:
        stabs = [line.strip() for line in f if line.strip()]

    # Flatten instructions to operations
    ops = []
    for instr in c:
        if instr.name == "CX":
            targets = instr.targets_copy()
            for k in range(0, len(targets), 2):
                ops.append(("CX", targets[k].value, targets[k+1].value))
        else:
            ops.append((instr.name, instr.targets_copy()))

    new_ops = []
    i = 0
    swap_count = 0
    while i < len(ops):
        # Check for SWAP: CX a b, CX b a, CX a b
        if i + 2 < len(ops):
            op1 = ops[i]
            op2 = ops[i+1]
            op3 = ops[i+2]
            
            if (op1[0] == "CX" and op2[0] == "CX" and op3[0] == "CX"):
                a1, b1 = op1[1], op1[2]
                a2, b2 = op2[1], op2[2]
                a3, b3 = op3[1], op3[2]
                
                if (a1 == b2 and b1 == a2 and a1 == a3 and b1 == b3):
                    # Found SWAP (a1, b1)
                    # Check if allowed? Yes.
                    new_ops.append(("SWAP", [a1, b1]))
                    i += 3
                    swap_count += 1
                    continue
        
        # Check for Cancel: CX a b, CX a b -> Identity
        if i + 1 < len(ops):
            op1 = ops[i]
            op2 = ops[i+1]
            if (op1[0] == "CX" and op2[0] == "CX"):
                if (op1[1] == op2[1] and op1[2] == op2[2]):
                    # Cancel
                    i += 2
                    continue
        
        # If not matched, keep
        new_ops.append(ops[i])
        i += 1
        
    print(f"Found {swap_count} SWAP replacements.")

    # Reconstruct
    new_c = stim.Circuit()
    for op in new_ops:
        name = op[0]
        
        if name == "CX":
            # op = ("CX", a, b)
            new_c.append("CX", [op[1], op[2]])
        elif name == "SWAP":
             # op = ("SWAP", [a, b])
             new_c.append("SWAP", op[1])
        else:
            # op = (name, targets)
            new_c.append(name, op[1])
            
    new_cx, new_vol = count_metrics(new_c)
    print(f"Optimized Metrics: CX={new_cx}, Vol={new_vol}")
    
    # Check preservation
    p = check_preservation(new_c, stabs)
    print(f"Preserved {p}/{len(stabs)}")
    
    if p == len(stabs):
        print("Preservation VERIFIED.")
        
        # Decompose long instructions to avoid wrapping
        final_c = stim.Circuit()
        for instr in new_c:
            if instr.name in ["CX", "SWAP"]:
                targets = instr.targets_copy()
                for k in range(0, len(targets), 2):
                    final_c.append(instr.name, [targets[k].value, targets[k+1].value])
            elif instr.name == "H":
                 targets = instr.targets_copy()
                 for t in targets:
                     final_c.append("H", [t.value])
            else:
                 final_c.append(instr)
                 
        with open("candidate_swap.stim", "w") as f:
            f.write(str(final_c))
    else:
        print("Preservation FAILED.")

if __name__ == "__main__":
    optimize()
