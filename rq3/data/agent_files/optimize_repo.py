import stim

def commutes(op1, op2):
    targets1 = set(t.value for t in op1.targets_copy() if t.is_qubit_target)
    targets2 = set(t.value for t in op2.targets_copy() if t.is_qubit_target)
    if targets1.isdisjoint(targets2):
        return True
    
    if op1.name == op2.name and op1.targets_copy() == op2.targets_copy():
        return True
        
    if op1.name == "CX" and op2.name == "CX":
        t1 = op1.targets_copy()
        t2 = op2.targets_copy()
        if len(t1) == 2 and len(t2) == 2:
            c1, t_1 = t1[0].value, t1[1].value
            c2, t_2 = t2[0].value, t2[1].value
            if c1 == c2 and t_1 != t_2:
                return True
            if t_1 == t_2 and c1 != c2:
                return True
                
    if op1.name == "H" and op2.name == "H":
        return True # Disjoint check covers this usually, but H is single qubit.
    
    return False

def is_inverse(op1, op2):
    if op1.name != op2.name:
        return False
    if op1.targets_copy() != op2.targets_copy():
        return False
    if op1.name in ["H", "CX", "CNOT", "X", "Y", "Z", "CY", "CZ", "SWAP"]:
        return True
    return False

def count_cx(circuit):
    cx = 0
    for op in circuit:
        if op.name in ["CX", "CNOT", "CY", "CZ"]:
            cx += len(op.targets_copy()) // 2
    return cx

def optimize():
    try:
        with open("baseline.stim", "r") as f:
            baseline = stim.Circuit(f.read())
    except:
        print("Could not read baseline")
        return

    print(f"Initial CX: {count_cx(baseline)}")
    
    ops = []
    for instr in baseline:
        if instr.name in ["CX", "CNOT", "H", "X", "Y", "Z", "CY", "CZ", "SWAP"]:
            targets = instr.targets_copy()
            if instr.name in ["CX", "CNOT", "CY", "CZ", "SWAP"]:
                arity = 2
            else:
                arity = 1
                
            for i in range(0, len(targets), arity):
                sub_targets = targets[i:i+arity]
                ops.append(stim.CircuitInstruction(instr.name, sub_targets, instr.gate_args_copy()))
        else:
            ops.append(instr)
            
    print(f"Expanded to {len(ops)} ops")
    
    changed = True
    while changed:
        changed = False
        new_ops = []
        skip_indices = set()
        
        for i in range(len(ops)):
            if i in skip_indices:
                continue
            
            op = ops[i]
            cancelled = False
            
            for j in range(i + 1, len(ops)):
                if j in skip_indices:
                    continue
                
                other = ops[j]
                
                if is_inverse(op, other):
                    blocked = False
                    for k in range(i + 1, j):
                        if k in skip_indices:
                            continue
                        if not commutes(op, ops[k]):
                            blocked = True
                            break
                    
                    if not blocked:
                        print(f"Cancelling {op} at {i} and {other} at {j}")
                        skip_indices.add(i)
                        skip_indices.add(j)
                        changed = True
                        cancelled = True
                        break
                
                if not commutes(op, other):
                    break
            
            if not cancelled:
                pass

        filtered_ops = []
        for i in range(len(ops)):
            if i not in skip_indices:
                filtered_ops.append(ops[i])
        ops = filtered_ops
        
        if changed:
            print(f"Optimized pass. Ops remaining: {len(ops)}")

    final_circ = stim.Circuit()
    for op in ops:
        final_circ.append(op)
        
    print(f"Final CX: {count_cx(final_circ)}")
    
    with open("cleaned_candidate_repo.stim", "w") as f:
        f.write(str(final_circ))

if __name__ == "__main__":
    optimize()
