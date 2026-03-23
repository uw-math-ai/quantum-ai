import stim
import collections
import sys
from analyze_my import analyze_faults_brute_force

def find_cover(circuit_file, stabilizers_file, threshold=3):
    print("Analyzing faults...")
    # Use existing analysis
    # analyze_faults_brute_force returns (dangerous_ops, undetectable_dangerous)
    # dangerous_ops is dict: op_idx -> list of (q, p, w, commutes_all)
    dangerous_ops, undetectable = analyze_faults_brute_force(circuit_file, stabilizers_file, threshold)
    
    print(f"Found {len(dangerous_ops)} locations with dangerous faults.")
    
    stabilizers = []
    with open(stabilizers_file, 'r') as f:
        for line in f:
            if line.strip():
                stabilizers.append(stim.PauliString(line.strip()))
                
    # Flatten dangerous ops to a list of faults
    faults = []
    for k, v in dangerous_ops.items():
        for item in v:
            # item is (q, p, w, commutes_all, res)
            faults.append(item + (k,))
            
    print(f"Processing {len(faults)} faults...")
    
    # Map each stabilizer to the set of faults it detects
    stab_to_faults = collections.defaultdict(set)
    fault_detected_by = collections.defaultdict(set)
    undetected_faults = []
    
    for f_idx, (q, p, w, comm, res, op_idx) in enumerate(faults):
        detectors = []
        for s_idx, s in enumerate(stabilizers):
            if not s.commutes(res):
                detectors.append(s_idx)
                stab_to_faults[s_idx].add(f_idx)
        
        if not detectors:
            undetected_faults.append(f_idx)
        else:
            for s_idx in detectors:
                fault_detected_by[f_idx].add(s_idx)
                
    if undetected_faults:
        print(f"WARNING: {len(undetected_faults)} faults are NOT detected by any stabilizer!")
        for f_idx in undetected_faults:
            q, p, w, comm, res, op_idx = faults[f_idx]
            print(f"Undetected Fault: Op {op_idx}, Qubit {q}, Pauli {p}, Weight {w}")
        
    print(f"Covering {len(fault_detected_by)} faults with stabilizers...")
    
    # Greedy cover
    universe = set(fault_detected_by.keys())
    covered = set()
    chosen_stabilizers = []
    
    while len(covered) < len(universe):
        # Find stabilizer that covers most uncovered faults
        best_s = -1
        best_count = -1
        
        # Iterate over all stabilizers that cover at least one uncovered fault
        # We can iterate over stab_to_faults
        
        current_best_s = None
        current_best_gain = -1
        
        for s_idx, f_set in stab_to_faults.items():
            # Calculate gain: how many faults in f_set are NOT in covered
            gain = len(f_set - covered)
            if gain > current_best_gain:
                current_best_gain = gain
                current_best_s = s_idx
                
        if current_best_gain <= 0:
            break
            
        chosen_stabilizers.append(current_best_s)
        covered.update(stab_to_faults[current_best_s])
        print(f"Selected stabilizer {current_best_s} (covers {current_best_gain} new faults)")
        
    print(f"Selected {len(chosen_stabilizers)} stabilizers to cover all detectable faults.")
    return chosen_stabilizers

if __name__ == '__main__':
    circuit_file = r'C:\Users\anpaz\Repos\quantum-ai\rq2\data\gemini-3-pro-preview\agent_files_ft\input_circuit.stim'
    stabs_file = r'C:\Users\anpaz\Repos\quantum-ai\rq2\data\gemini-3-pro-preview\agent_files_ft\stabilizers_rq2.txt'
    
    chosen = find_cover(circuit_file, stabs_file, threshold=3)
    print("Chosen stabilizers indices:", chosen)
    
    # Save chosen indices
    with open(r'C:\Users\anpaz\Repos\quantum-ai\rq2\data\gemini-3-pro-preview\agent_files_ft\chosen_stabilizers.txt', 'w') as f:
        for idx in chosen:
            f.write(str(idx) + '\n')
