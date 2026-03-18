import stim
import sys

def expand_circuit(circuit):
    expanded = []
    for instr in circuit:
        if instr.name in ["CX", "CNOT", "CY", "CZ", "SWAP", "ISWAP"]:
            targets = instr.targets_copy()
            for i in range(0, len(targets), 2):
                expanded.append(stim.CircuitInstruction(instr.name, targets[i:i+2], instr.gate_args_copy()))
        elif instr.name in ["H", "S", "X", "Y", "Z", "I"]:
            targets = instr.targets_copy()
            for t in targets:
                expanded.append(stim.CircuitInstruction(instr.name, [t], instr.gate_args_copy()))
        else:
             expanded.append(instr)
    return expanded

def identify_swaps(instructions):
    new_instrs = []
    i = 0
    while i < len(instructions):
        if i + 2 < len(instructions):
            op1 = instructions[i]
            op2 = instructions[i+1]
            op3 = instructions[i+2]
            if op1.name == "CX" and op2.name == "CX" and op3.name == "CX":
                t1 = op1.targets_copy()
                t2 = op2.targets_copy()
                t3 = op3.targets_copy()
                a, b = t1[0].value, t1[1].value
                # Check for CX a b; CX b a; CX a b
                # t2 should be b->a. t3 should be a->b.
                if (t2[0].value == b and t2[1].value == a and
                    t3[0].value == a and t3[1].value == b):
                    # Found SWAP a b
                    new_instrs.append(stim.CircuitInstruction("SWAP", [t1[0], t1[1]], op1.gate_args_copy()))
                    i += 3
                    continue
        new_instrs.append(instructions[i])
        i += 1
    return new_instrs

def optimize_swaps(instructions):
    current = list(instructions)
    changed = True
    while changed:
        changed = False
        new_list = []
        i = 0
        while i < len(current):
            matched = False
            if i + 1 < len(current):
                op1 = current[i]
                op2 = current[i+1]
                
                # SWAP-SWAP
                if op1.name == "SWAP" and op2.name == "SWAP":
                    t1 = op1.targets_copy()
                    t2 = op2.targets_copy()
                    u1, v1 = t1[0].value, t1[1].value
                    u2, v2 = t2[0].value, t2[1].value
                    if {u1, v1} == {u2, v2}:
                        # Cancel
                        i += 2
                        changed = True
                        matched = True
                
                if not matched and ((op1.name == "CX" and op2.name == "SWAP") or 
                                    (op1.name == "SWAP" and op2.name == "CX")):
                    # CX u v; SWAP u v (or v u) -> CX v u
                    # SWAP u v; CX u v (or v u) -> CX v u
                    
                    t1 = op1.targets_copy()
                    t2 = op2.targets_copy()
                    u1, v1 = t1[0].value, t1[1].value
                    u2, v2 = t2[0].value, t2[1].value
                    
                    # Check if same pair
                    if {u1, v1} == {u2, v2}:
                        # Replace with CX v u
                        # If op1 is CX: targets are u, v. New CX targets v, u.
                        # If op1 is SWAP: op2 is CX(u, v). New CX targets v, u.
                        
                        # Wait, logic:
                        # CX(c, t) followed by SWAP(c, t) -> CX(t, c).
                        # Let's verify direction.
                        # CX 0 1; SWAP 0 1. (0->1, 1->0).
                        # State |10>. CX->|10>. SWAP->|01>.
                        # CX 1 0 on |10> -> |11>.
                        # Is it CX 1 0?
                        # Start |01>. CX->|01>. SWAP->|10>.
                        # CX 1 0 on |01> -> |01>.
                        # Start |11>. CX->|10>. SWAP->|01>.
                        # CX 1 0 on |11> -> |10>.
                        # Start |00>. CX->|00>. SWAP->|00>.
                        # CX 1 0 on |00> -> |00>.
                        # Matches!
                        # So CX(c, t); SWAP(c, t) -> CX(t, c).
                        
                        control, target = -1, -1
                        if op1.name == "CX":
                            control, target = t1[0].value, t1[1].value
                        else:
                            control, target = t2[0].value, t2[1].value
                        
                        new_targets = [target, control] # Swap indices
                        new_list.append(stim.CircuitInstruction("CX", new_targets, []))
                        i += 2
                        changed = True
                        matched = True

            if not matched:
                new_list.append(current[i])
                i += 1
                
        current = new_list
        
    return current

def solve():
    with open("data/agent_files/baseline.stim", "r") as f:
        baseline_text = f.read()
    
    with open("data/agent_files/stabilizers.txt", "r") as f:
        stabs = [line.strip() for line in f if line.strip()]

    baseline = stim.Circuit(baseline_text)
    expanded = expand_circuit(baseline)
    
    # Identify SWAPs
    swapped = identify_swaps(expanded)
    
    # Optimize SWAPs
    optimized = optimize_swaps(swapped)
    
    # Construct final
    final_circuit = stim.Circuit()
    for instr in optimized:
        final_circuit.append(instr)
        
    # Validation
    sim = stim.TableauSimulator()
    sim.do(final_circuit)
    valid = True
    for s_str in stabs:
        if sim.peek_observable_expectation(stim.PauliString(s_str)) != 1:
            valid = False
            break
            
    print(f"Valid: {valid}")
    
    # Metrics
    cx = 0
    vol = 0
    for instr in optimized:
        if instr.name == "CX":
            cx += 1
            vol += 1
        elif instr.name == "SWAP":
            cx += 3 # Conservative
            vol += 1 # Optimistic but likely correct for volume
        else:
            vol += 1
            
    print(f"Est Metrics: CX={cx}, Vol={vol}")
    
    with open("data/agent_files/candidate.stim", "w") as f:
        f.write(str(final_circuit))

if __name__ == "__main__":
    solve()
