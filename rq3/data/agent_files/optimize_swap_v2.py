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
        c = stim.Circuit(f.read())
        
    base_cx, base_vol = count_metrics(c)
    print(f"Baseline Metrics: CX={base_cx}, Vol={base_vol}")
    
    # Load Stabilizers
    with open("target_stabilizers.txt", "r") as f:
        stabs = [line.strip() for line in f if line.strip()]

    # Check baseline preservation
    if check_preservation(c, stabs) != len(stabs):
        print("WARNING: Baseline does not preserve all stabilizers!")

    # Flatten instructions to operations
    ops = []
    for instr in c:
        if instr.name == "CX":
            targets = instr.targets_copy()
            for i in range(0, len(targets), 2):
                ops.append(("CX", targets[i].value, targets[i+1].value))
        else:
            ops.append((instr.name, instr.targets_copy()))

    new_ops = []
    i = 0
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
                    print(f"Found SWAP replacement candidate: {a1} <-> {b1}")
                    new_ops.append(("SWAP", [stim.target_rec(a1), stim.target_rec(b1)])) # Wait, target_rec is internal? 
                    # Use integer targets for simplicity in reconstruction
                    # Stim requires correct target types.
                    # Actually, if I store targets as list of ints, I can reconstruct.
                    # But stim targets can be qubits or measurements. Here just qubits.
                    
                    # Store as ("SWAP", [a1, b1])
                    new_ops.append(("SWAP", [a1, b1]))
                    i += 3
                    continue
        
        # If not SWAP, append current op
        new_ops.append(ops[i])
        i += 1
        
    # Reconstruct
    new_c = stim.Circuit()
    for op in new_ops:
        name = op[0]
        targets = op[1]
        
        if name == "CX":
            # targets are a, b
            new_c.append("CX", [targets[0], targets[1]])
        elif name == "SWAP":
             new_c.append("SWAP", [targets[0], targets[1]])
        else:
            # name is string, targets is list of Target objects
            # Need to pass list of targets.
            # stim.Circuit.append takes targets
            new_c.append(name, targets)
            
    new_cx, new_vol = count_metrics(new_c)
    print(f"Optimized Metrics: CX={new_cx}, Vol={new_vol}")
    
    # Check preservation
    if check_preservation(new_c, stabs) == len(stabs):
        print("Preservation VERIFIED.")
        with open("candidate_swap.stim", "w") as f:
            f.write(str(new_c))
    else:
        print("Preservation FAILED.")

if __name__ == "__main__":
    optimize()
