import json

def get_stabilizers():
    stabs = [
        "XXIXXIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIII", "IIIIIIIIIXXIXXIIIIIIIIIIIIIIIIIIIIIIIIIIIIIII", "IIIIIIIIIIIIIIIIIIXXIXXIIIIIIIIIIIIIIIIIIIIII", "IIIIIIIIIIIIIIIIIIIIIIIIIIIXXIXXIIIIIIIIIIIII", "IIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIXXIXXIIII", "IIIIXXIXXIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIII", "IIIIIIIIIIIIIXXIXXIIIIIIIIIIIIIIIIIIIIIIIIIII", "IIIIIIIIIIIIIIIIIIIIIIXXIXXIIIIIIIIIIIIIIIIII", "IIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIXXIXXIIIIIIIII", "IIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIXXIXX", "IIXIIXIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIII", "IIIIIIIIIIIXIIXIIIIIIIIIIIIIIIIIIIIIIIIIIIIII", "IIIIIIIIIIIIIIIIIIIIXIIXIIIIIIIIIIIIIIIIIIIII", "IIIIIIIIIIIIIIIIIIIIIIIIIIIIIXIIXIIIIIIIIIIII", "IIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIXIIXIII", "IIIXIIXIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIII", "IIIIIIIIIIIIXIIXIIIIIIIIIIIIIIIIIIIIIIIIIIIII", "IIIIIIIIIIIIIIIIIIIIIXIIXIIIIIIIIIIIIIIIIIIII", "IIIIIIIIIIIIIIIIIIIIIIIIIIIIIIXIIXIIIIIIIIIII", "IIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIXIIXII", "IIIZZIZZIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIII", "IIIIIIIIIIIIZZIZZIIIIIIIIIIIIIIIIIIIIIIIIIIII", "IIIIIIIIIIIIIIIIIIIIIZZIZZIIIIIIIIIIIIIIIIIII", "IIIIIIIIIIIIIIIIIIIIIIIIIIIIIIZZIZZIIIIIIIIII", "IIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIZZIZZI", "IZZIZZIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIII", "IIIIIIIIIIZZIZZIIIIIIIIIIIIIIIIIIIIIIIIIIIIII", "IIIIIIIIIIIIIIIIIIIZZIZZIIIIIIIIIIIIIIIIIIIII", "IIIIIIIIIIIIIIIIIIIIIIIIIIIIZZIZZIIIIIIIIIIII", "IIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIZZIZZIII", "ZZIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIII", "IIIIIIIIIZZIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIII", "IIIIIIIIIIIIIIIIIIZZIIIIIIIIIIIIIIIIIIIIIIIII", "IIIIIIIIIIIIIIIIIIIIIIIIIIIZZIIIIIIIIIIIIIIII", "IIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIZZIIIIIII", "IIIIIIIZZIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIII", "IIIIIIIIIIIIIIIIZZIIIIIIIIIIIIIIIIIIIIIIIIIII", "IIIIIIIIIIIIIIIIIIIIIIIIIZZIIIIIIIIIIIIIIIIII", "IIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIZZIIIIIIIII", "IIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIZZ", "IIXXXIIIIZIIZIIZIIZIIZIIZIIIIXXXIIIIIIIIIIIII", "IIIIIIIIIIIXXXIIIIZIIZIIZIIZIIZIIZIIIIXXXIIII", "IIXXXIIIIIIIIIIIIIIIXXXIIIIZIIZIIZIIZIIZIIZII", "ZIIZIIZIIIIXXXIIIIIIIIIIIIIIIXXXIIIIZIIZIIZII"
    ]
    return stabs

def check_anticommute(stab, error_paulis):
    # stab is a string "XXI..."
    # error_paulis is a dict { "0": "X", ... }
    commute = True # 0 means commute, 1 means anti-commute. Let's trace phase.
    # Actually, two Paulis anti-commute if they differ in X/Z components on an odd number of qubits.
    # X and Z anti-commute. X and Y anti-commute. Y and Z anti-commute.
    # I and anything commute. Same Pauli commute.
    
    anti_commutes_count = 0
    for i, char in enumerate(stab):
        if i >= 45: break
        p_stab = char
        p_err = error_paulis.get(str(i), "I")
        
        if p_stab == "I" or p_err == "I":
            continue
        if p_stab == p_err:
            continue
        # If different non-identity, they anti-commute
        anti_commutes_count += 1
        
    return (anti_commutes_count % 2) == 1

def analyze():
    with open(r"data\gemini-3-pro-preview\agent_files_ft\last_validation.json", "r") as f:
        data = json.load(f)
        
    errors = data.get("error_propagation", [])
    stabs = get_stabilizers()
    
    # Calculate weights
    stab_weights = {}
    for i, s in enumerate(stabs):
        w = 0
        for char in s:
            if char != 'I': w += 1
        stab_weights[i] = w
    
    print(f"Analyzing {len(errors)} errors...")
    
    # error_id -> error object
    error_map = {i: e for i, e in enumerate(errors)}
    remaining_errors = set(error_map.keys())
    
    selected_stabs = []
    
    # Strategy: Weight first.
    # Sort stabilizers by weight.
    sorted_stabs = sorted(range(len(stabs)), key=lambda k: stab_weights[k])
    
    while remaining_errors:
        best_stab = None
        best_covered = set()
        
        # Iterate through sorted stabilizers to find the first one that covers ANY new error
        # Actually, we want the one that covers the MOST new errors among the low weight ones?
        # Let's just iterate and pick the first one that provides non-zero coverage.
        # This gives priority to low weight.
        # But if a weight 2 covers 1 error, and weight 4 covers 10...
        # Maybe we should group by weight.
        
        # Let's try: Find best coverage among lowest weight class that has coverage.
        
        found = False
        for s_idx in sorted_stabs:
            if any(x[0] == s_idx for x in selected_stabs): continue
            
            s = stabs[s_idx]
            covered = set()
            for e_id in remaining_errors:
                err = error_map[e_id]
                if check_anticommute(s, err["final_paulis"]):
                    covered.add(e_id)
            
            if covered:
                # Found a stabilizer (lowest weight because sorted) that covers something.
                # Is it the best *within this weight*?
                # The current loop order is by weight.
                # So s_idx has minimal weight.
                # But there might be other stabilizers with same weight that cover MORE.
                # So we should check all stabs with same weight.
                
                # Let's define "best" as: maximize coverage, minimize weight.
                # But since we iterate by weight, we just need to maximize coverage within the current weight.
                
                current_weight = stab_weights[s_idx]
                
                # Check all stabs with this weight
                candidates = [k for k in sorted_stabs if stab_weights[k] == current_weight]
                
                best_in_class = None
                max_cov = 0
                best_cov_set = set()
                
                for cand in candidates:
                    if any(x[0] == cand for x in selected_stabs): continue
                    c_cov = set()
                    for e_id in remaining_errors:
                        if check_anticommute(stabs[cand], error_map[e_id]["final_paulis"]):
                            c_cov.add(e_id)
                    if len(c_cov) > max_cov:
                        max_cov = len(c_cov)
                        best_in_class = cand
                        best_cov_set = c_cov
                
                best_stab = best_in_class
                best_covered = best_cov_set
                found = True
                break
        
        if not found:
            print("Cannot cover remaining errors!")
            break
            
        print(f"Stabilizer {best_stab} (weight {stab_weights[best_stab]}) covers {len(best_covered)} errors: {list(best_covered)}")
        selected_stabs.append((best_stab, stabs[best_stab]))
        remaining_errors -= best_covered
        
    print("\nSelected stabilizers:")
    for i, (idx, s) in enumerate(selected_stabs):
        print(f"{i}: Index {idx}, {s}")

if __name__ == "__main__":
    analyze()
