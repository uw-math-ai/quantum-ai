import stim

def main():
    with open("target_stabilizers_FIXED_FINAL.txt", "r") as f:
        lines = [l.strip() for l in f if l.strip()]
    
    print(f"Total non-empty lines: {len(lines)}")
    
    stabs = [stim.PauliString(s) for s in lines]
    
    # Check full set consistency
    try:
        stim.Tableau.from_stabilizers(stabs, allow_underconstrained=True)
        print("All stabilizers are consistent!")
        return
    except Exception as e:
        print(f"Inconsistent: {e}")

    # Greedy approach to find max consistent subset
    consistent = []
    for i, s in enumerate(stabs):
        candidate = consistent + [s]
        try:
            stim.Tableau.from_stabilizers(candidate, allow_underconstrained=True)
            consistent.append(s)
        except:
            print(f"Dropping stabilizer {i}")
            
    print(f"Max consistent size (forward greedy): {len(consistent)}")
    
    # Try reverse greedy
    consistent_rev = []
    for i, s in enumerate(reversed(stabs)):
        candidate = consistent_rev + [s]
        try:
            stim.Tableau.from_stabilizers(candidate, allow_underconstrained=True)
            consistent_rev.append(s)
        except:
            print(f"Dropping stabilizer {len(stabs)-1-i} (reverse)")
            
    print(f"Max consistent size (reverse greedy): {len(consistent_rev)}")
    
    # If reverse is better, use it.
    
    best_stabs = consistent if len(consistent) >= len(consistent_rev) else consistent_rev
    
    # Synthesize
    tableau = stim.Tableau.from_stabilizers(best_stabs, allow_underconstrained=True)
    circ = tableau.to_circuit(method="graph_state")
    
    with open("candidate_fixed_max.stim", "w") as f:
        f.write(str(circ))
    print("Saved candidate_fixed_max.stim")

if __name__ == "__main__":
    main()
