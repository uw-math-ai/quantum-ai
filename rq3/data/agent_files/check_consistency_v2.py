import stim
import re

def check():
    with open("current_target_stabilizers.txt", "r") as f:
        lines = [l.strip().strip(',') for l in f if l.strip()]
    
    print(f"Loaded {len(lines)} stabilizers.")
    
    try:
        stabs = [stim.PauliString(s) for s in lines]
    except Exception as e:
        print(f"Error parsing stabilizers: {e}")
        return

    anticommuting_pairs = []
    for i in range(len(stabs)):
        for j in range(i + 1, len(stabs)):
            if not stabs[i].commutes(stabs[j]):
                anticommuting_pairs.append((i, j))
    
    if anticommuting_pairs:
        print(f"Found {len(anticommuting_pairs)} anticommuting pairs!")
        for i, j in anticommuting_pairs[:3]:
            print(f"  {i} vs {j}")
            print(f"  {stabs[i]}")
            print(f"  {stabs[j]}")
    else:
        print("All stabilizers commute.")

    # Check baseline
    with open("current_baseline.stim", "r") as f:
        base_circ = stim.Circuit(f.read())
        
    sim = stim.TableauSimulator()
    sim.do(base_circ)
    
    preserved = 0
    for s in stabs:
        if sim.peek_observable_expectation(s) == 1:
            preserved += 1
            
    print(f"Baseline preserves {preserved}/{len(stabs)} stabilizers.")

if __name__ == "__main__":
    check()
