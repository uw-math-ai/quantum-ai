import stim
import json

def main():
    # Load stabilizers
    with open(r"C:\Users\anpaz\Repos\quantum-ai\rq2\data\gemini-3-pro-preview\agent_files_ft\stabilizers.txt", "r") as f:
        stab_strs = f.read().strip().split('\n')
    
    stabs = [stim.PauliString(s) for s in stab_strs]
    
    # Calculate weights
    stab_weights = {}
    for i, s in enumerate(stabs):
        w = 0
        for k in range(len(s)):
            if s[k] != 0: w += 1
        stab_weights[i] = w
        
    # Load faults
    with open(r"C:\Users\anpaz\Repos\quantum-ai\rq2\data\gemini-3-pro-preview\agent_files_ft\bad_faults.txt", "r") as f:
        faults = json.load(f)
        
    print(f"Loaded {len(faults)} faults.")
    
    fault_detectors = {}
    undetectable_faults = []
    
    for fault in faults:
        p_str = fault['final_pauli']
        p = stim.PauliString(p_str)
        
        detectors = []
        for i, s in enumerate(stabs):
            if not p.commutes(s):
                detectors.append(i)
        
        if detectors:
            fault_detectors[str(fault)] = detectors
        else:
            undetectable_faults.append(fault)
            
    print(f"Undetectable faults (harmless or logical): {len(undetectable_faults)}")
    if undetectable_faults:
        print("Example undetectable fault:")
        f0 = undetectable_faults[0]
        print(f"Error: {f0['error']} on {f0['qubit']} at {f0['index']}")
        print(f"Final Pauli: {f0['final_pauli']}")
        print(f"Weight: {f0['weight']}")
        
    # Solve Set Cover with preference for low weight
    universe = set(fault_detectors.keys())
    remaining_faults = universe.copy()
    
    selected_stabilizers = []
    
    # Group stabilizers by weight
    low_weight_candidates = [i for i in range(len(stabs)) if stab_weights[i] <= 4]
    high_weight_candidates = [i for i in range(len(stabs)) if stab_weights[i] > 4]
    
    def run_greedy(candidates, current_remaining):
        selected = []
        while current_remaining:
            best_stab = -1
            max_c = 0
            
            for s_idx in candidates:
                if s_idx in selected or s_idx in selected_stabilizers: continue
                c = 0
                for f_key in current_remaining:
                    if s_idx in fault_detectors[f_key]:
                        c += 1
                if c > max_c:
                    max_c = c
                    best_stab = s_idx
            
            if max_c == 0:
                break
                
            selected.append(best_stab)
            # Update remaining local copy? No, update current_remaining set
            to_remove = []
            for f_key in current_remaining:
                if best_stab in fault_detectors[f_key]:
                    to_remove.append(f_key)
            for k in to_remove:
                current_remaining.remove(k)
        return selected

    print("Attempting to cover with low weight (<=4) stabilizers...")
    s1 = run_greedy(low_weight_candidates, remaining_faults)
    selected_stabilizers.extend(s1)
    
    if remaining_faults:
        print(f"{len(remaining_faults)} faults remain. Using high weight stabilizers.")
        s2 = run_greedy(high_weight_candidates, remaining_faults)
        selected_stabilizers.extend(s2)
            
    print(f"Selected {len(selected_stabilizers)} stabilizers to measure.")
    print("Indices:", selected_stabilizers)
    
    with open(r"C:\Users\anpaz\Repos\quantum-ai\rq2\data\gemini-3-pro-preview\agent_files_ft\stabilizers_to_measure.txt", "w") as f:
        f.write(",".join(map(str, selected_stabilizers)))

if __name__ == "__main__":
    main()
