import stim
import sys

def load_bad_faults():
    # We will just re-run the analysis as it is easier than parsing the text file with eval
    # Or actually, we can import the function
    from find_bad_faults import analyze_faults
    return analyze_faults('input.stim', 3)

def find_cover():
    print("Analyzing faults...")
    bad_faults = load_bad_faults()
    print(f"Found {len(bad_faults)} bad faults.")
    
    stabilizers = []
    with open('stabilizers.txt', 'r') as f:
        for line in f:
            if line.strip():
                stabilizers.append(stim.PauliString(line.strip()))
                
    # Check coverage
    # Map each stabilizer to the set of faults it detects
    # Map each fault to the set of stabilizers that detect it
    
    print("Computing detection matrix...")
    fault_detected_by = []
    
    # We only need the error string from the fault
    # Convert string to PauliString
    # The error string in dict is like "+___XX..."
    
    import collections
    
    undetected_faults = []
    
    stab_tableau = stim.Tableau.from_stabilizers(stabilizers, allow_redundant=True, allow_underconstrained=True)
    inv_stab_tableau = stab_tableau.inverse()
    
    def is_stabilizer(p):
        p_slice = p[:135]
        p_mapped = inv_stab_tableau(p_slice)
        s = str(p_mapped)
        return 'X' not in s and 'Y' not in s

    for i, f in enumerate(bad_faults):
        p_str = f['error_string']
        p = stim.PauliString(p_str)
        
        # Verify it is not a stabilizer (should have been filtered, but double check)
        if is_stabilizer(p):
            continue
            
        detectors = []
        for s_idx, s in enumerate(stabilizers):
            if not p.commutes(s):
                detectors.append(s_idx)
        
        if not detectors:
            undetected_faults.append(i)
        else:
            fault_detected_by.append(set(detectors))
            
    if undetected_faults:
        print(f"WARNING: {len(undetected_faults)} faults are NOT detected by any stabilizer!")
        # These are logical errors (weight >= 4 but commute).
        # We cannot fix them by measuring stabilizers.
        # We must flag them proactively.
        # Or maybe they are stabilizers?
        # If they commute with ALL stabilizers, they are either stabilizers or logical operators.
        # If weight < distance (9), they shouldn't be logical.
        # So they must be stabilizers.
        # But analyze_faults filters stabilizers.
        # Maybe is_stabilizer check is imperfect?
    
    print(f"Covering {len(fault_detected_by)} faults with stabilizers...")
    
    # Greedy cover
    universe = set(range(len(fault_detected_by)))
    covered = set()
    chosen_stabilizers = []
    
    while len(covered) < len(universe):
        # Find stabilizer that covers most uncovered faults
        best_s = -1
        best_count = -1
        
        # Count how many uncovered faults each stabilizer covers
        # This is slow if we iterate stabilizers.
        # Invert the map: stabilizer -> faults
        stab_to_faults = collections.defaultdict(set)
        for f_idx, s_set in enumerate(fault_detected_by):
            if f_idx not in covered:
                for s in s_set:
                    stab_to_faults[s].add(f_idx)
        
        if not stab_to_faults:
            break
            
        best_s = max(stab_to_faults, key=lambda s: len(stab_to_faults[s]))
        count = len(stab_to_faults[best_s])
        
        chosen_stabilizers.append(best_s)
        covered.update(stab_to_faults[best_s])
        print(f"Selected stabilizer {best_s} (covers {count} new faults)")
        
    print(f"Selected {len(chosen_stabilizers)} stabilizers to cover all detectable faults.")
    
    return chosen_stabilizers, undetected_faults

if __name__ == '__main__':
    chosen, undetected = find_cover()
    print("Chosen stabilizers indices:", chosen)
    if undetected:
        print("Undetected faults indices:", undetected)
    
    # Write chosen to file
    with open('chosen_stabilizers.txt', 'w') as f:
        for idx in chosen:
            f.write(str(idx) + '\n')
