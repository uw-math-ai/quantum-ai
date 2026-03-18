import stim

def check_prefix():
    # Load baseline stabilizers
    with open("current_task_baseline.stim", "r") as f:
        baseline = stim.Circuit(f.read())
    
    # Get canonical stabilizers from baseline
    sim = stim.TableauSimulator()
    sim.do(baseline)
    base_stabs = sim.canonical_stabilizers()
    
    # Load prompt stabilizers
    with open("target_stabilizers_prompt.txt", "r") as f:
        prompt_lines = [l.strip() for l in f if l.strip()]
        
    print(f"Baseline has {len(base_stabs)} stabilizers.")
    print(f"Prompt has {len(prompt_lines)} stabilizers.")
    
    # Convert to strings
    base_strs = [str(s) for s in base_stabs]
    
    matched_count = 0
    for p_line in prompt_lines:
        # p_line is like "IIX..."
        # base_str is like "+IIX..."
        # We need to ignore sign for prefix check? Or should match sign?
        # Prompt doesn't have sign.
        
        # Also, canonical stabilizers might be a different basis.
        # But if the prompt list is the "canonical" list, maybe they match?
        
        found = False
        for b_str in base_strs:
            # Strip sign
            clean_b = b_str[1:] if b_str[0] in "+-" else b_str
            
            # Check prefix
            if clean_b.startswith(p_line):
                found = True
                break
        
        if found:
            matched_count += 1
        else:
            # print(f"Prompt stabilizer not found as prefix: {p_line[:10]}...")
            pass
            
    print(f"Matched {matched_count}/{len(prompt_lines)} prompt stabilizers as prefixes.")

if __name__ == "__main__":
    check_prefix()
