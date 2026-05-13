import stim

def load_circuit(filename):
    with open(filename, 'r') as f:
        return stim.Circuit(f.read())

def replace_swaps(circuit):
    new_circuit = stim.Circuit()
    
    # We iterate through instructions.
    # We need to look ahead.
    # We can convert to a list of (name, targets) first.
    
    ops = []
    for instr in circuit:
        if instr.name == "CX":
            targets = instr.targets_copy()
            for k in range(0, len(targets), 2):
                ops.append(("CX", [targets[k].value, targets[k+1].value]))
        elif instr.name in ["H", "S", "X", "Y", "Z", "I"]:
            targets = instr.targets_copy()
            for t in targets:
                ops.append((instr.name, [t.value]))
        else:
            # Keep others as is (e.g. M, R)
            # But we might need to handle them carefully.
            # The input only has simple gates.
            ops.append((instr.name, [t.value for t in instr.targets_copy()]))

    i = 0
    while i < len(ops):
        # Check for SWAP pattern: CX a b; CX b a; CX a b
        if i + 2 < len(ops):
            op1 = ops[i]
            op2 = ops[i+1]
            op3 = ops[i+2]
            
            if (op1[0] == "CX" and op2[0] == "CX" and op3[0] == "CX"):
                t1 = op1[1]
                t2 = op2[1]
                t3 = op3[1]
                
                # Check indices
                # CX a b: t1=[a, b]
                # CX b a: t2=[b, a]
                # CX a b: t3=[a, b]
                
                if (t1[0] == t2[1] and t1[1] == t2[0] and
                    t1[0] == t3[0] and t1[1] == t3[1]):
                    # Found SWAP
                    new_circuit.append("SWAP", t1)
                    i += 3
                    continue
        
        # If not swap, append current op
        name, targs = ops[i]
        new_circuit.append(name, targs)
        i += 1
        
    return new_circuit

c = load_circuit("original.stim")
new_c = replace_swaps(c)
with open("candidate.stim", "w") as f:
    f.write(str(new_c))
    
print(f"Original ops: {len(c)}")
print(f"New ops: {len(new_c)}")
