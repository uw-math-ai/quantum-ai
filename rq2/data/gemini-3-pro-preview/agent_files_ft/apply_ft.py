import re

def parse_stim(content):
    lines = content.strip().split('\n')
    ops = []
    for line in lines:
        line = line.strip()
        if not line: continue
        parts = line.split()
        name = parts[0]
        args = [int(x) for x in parts[1:]]
        ops.append((name, args))
    return ops

def apply_ft(input_file, output_file):
    with open(input_file, 'r') as f:
        content = f.read()
    
    ops = parse_stim(content)
    new_lines = []
    
    # Find max qubit index to start ancillas
    max_q = 0
    for name, args in ops:
        for a in args:
            if a > max_q: max_q = a
    
    next_ancilla = max_q + 1
    
    def get_ancilla():
        nonlocal next_ancilla
        a = next_ancilla
        next_ancilla += 1
        return a
    
    for name, args in ops:
        if name == "CX":
            # args is list of integers c1, t1, c2, t2...
            pairs = []
            for i in range(0, len(args), 2):
                pairs.append((args[i], args[i+1]))
            
            # Group consecutive pairs with same control
            current_c = -1
            group_targets = []
            
            for c, t in pairs:
                if c != current_c:
                    # Flush previous group
                    if current_c != -1:
                        if len(group_targets) >= 2:
                            # Apply gadget
                            # Gadget: CopyVerify
                            # Alloc a, k
                            a = get_ancilla()
                            k = get_ancilla()
                            # Gates
                            # CX c a
                            new_lines.append(f"CX {current_c} {a}")
                            # Verify Zc Za: CX c k, CX a k, M k
                            new_lines.append(f"CX {current_c} {k} {a} {k}")
                            new_lines.append(f"M {k}")
                            # Detect: if k=1, error. (Implicit in FT score)
                            
                            # Distribute a
                            for gt in group_targets:
                                new_lines.append(f"CX {a} {gt}")
                            
                            # Uncompute a: CX c a
                            new_lines.append(f"CX {current_c} {a}")
                            # Measure a
                            new_lines.append(f"M {a}")
                        else:
                            # Single CX
                            t_single = group_targets[0]
                            new_lines.append(f"CX {current_c} {t_single}")
                    
                    current_c = c
                    group_targets = [t]
                else:
                    group_targets.append(t)
            
            # Flush last group
            if current_c != -1:
                if len(group_targets) >= 2:
                    a = get_ancilla()
                    k = get_ancilla()
                    new_lines.append(f"CX {current_c} {a}")
                    new_lines.append(f"CX {current_c} {k} {a} {k}")
                    new_lines.append(f"M {k}")
                    for gt in group_targets:
                        new_lines.append(f"CX {a} {gt}")
                    new_lines.append(f"CX {current_c} {a}")
                    new_lines.append(f"M {a}")
                else:
                    t_single = group_targets[0]
                    new_lines.append(f"CX {current_c} {t_single}")
                    
        else:
            # Other gates (H, etc)
            line = f"{name} " + " ".join(str(x) for x in args)
            new_lines.append(line)
            
    with open(output_file, 'w') as f:
        f.write('\n'.join(new_lines))

apply_ft(r"C:\Users\anpaz\Repos\quantum-ai\rq2\data\gemini-3-pro-preview\agent_files_ft\circuit_v2.stim", 
         r"C:\Users\anpaz\Repos\quantum-ai\rq2\data\gemini-3-pro-preview\agent_files_ft\circuit_ft_v2.stim")
