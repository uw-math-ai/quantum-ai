import stim
import sys
import collections

sys.path.append('.')
from find_bad_faults import analyze_faults

def load_bad_faults():
    return analyze_faults('input.stim', 3)

def find_cover():
    print("Analyzing faults...")
    bad_faults = load_bad_faults()
    print(f"Found {len(bad_faults)} bad faults.")
    
    stabilizers = []
    with open('all_stabilizers.txt', 'r') as f:
        for line in f:
            if line.strip():
                stabilizers.append(stim.PauliString(line.strip()))
                
    print("Computing detection matrix...")
    
    fault_coverage = [] # List of (fault_idx, detectors_set)
    undetected_faults = []
    
    for i, f in enumerate(bad_faults):
        p_str = f['error_string']
        p = stim.PauliString(p_str)
        
        detectors = set()
        for s_idx, s in enumerate(stabilizers):
            if not p.commutes(s):
                detectors.add(s_idx)
        
        if not detectors:
            undetected_faults.append(i)
        else:
            fault_coverage.append((i, detectors))
            
    if undetected_faults:
        print(f"WARNING: {len(undetected_faults)} faults are NOT detected by any stabilizer!")
        
    print(f"Covering {len(fault_coverage)} faults with stabilizers...")
    
    if not fault_coverage:
        return [], undetected_faults

    universe = set(idx for idx, _ in fault_coverage)
    covered = set()
    chosen_stabilizers = []
    
    stab_to_faults = collections.defaultdict(set)
    for f_idx, s_set in fault_coverage:
        for s in s_set:
            stab_to_faults[s].add(f_idx)
            
    while len(covered) < len(universe):
        best_s = -1
        best_new_count = -1
        
        for s, faults in stab_to_faults.items():
            if s in chosen_stabilizers:
                continue
            
            new_faults = faults - covered
            count = len(new_faults)
            
            if count > best_new_count:
                best_new_count = count
                best_s = s
        
        if best_new_count <= 0:
            break
            
        chosen_stabilizers.append(best_s)
        covered.update(stab_to_faults[best_s])
        print(f"Selected stabilizer {best_s} (covers {best_new_count} new faults)")
        
    print(f"Selected {len(chosen_stabilizers)} stabilizers to cover all detectable faults.")
    
    return chosen_stabilizers, undetected_faults

if __name__ == '__main__':
    chosen, undetected = find_cover()
    print("Chosen stabilizers indices:", chosen)
    if undetected:
        print("Undetected faults indices count:", len(undetected))
    
    with open('chosen_stabilizers_all.txt', 'w') as f:
        for idx in chosen:
            f.write(str(idx) + '\n')
