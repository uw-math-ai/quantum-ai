import stim
import sys

def check():
    # Load stabilizers
    with open("current_target_stabilizers.txt", "r") as f:
        content = f.read().replace('\n', '').replace(' ', '')
    
    stabs_str = [s for s in content.split(',') if s]
    print(f"Loaded {len(stabs_str)} stabilizers.")
    
    # Check consistency
    stabs = [stim.PauliString(s) for s in stabs_str]
    
    anticommuting_pairs = []
    for i in range(len(stabs)):
        for j in range(i + 1, len(stabs)):
            if stabs[i].commutes(stabs[j]) == False:
                anticommuting_pairs.append((i, j))
    
    if anticommuting_pairs:
        print(f"Found {len(anticommuting_pairs)} anticommuting pairs!")
        for i, j in anticommuting_pairs[:5]:
            print(f"  {i} vs {j}")
            print(f"  {stabs[i]}")
            print(f"  {stabs[j]}")
    else:
        print("All stabilizers commute.")

    # Check baseline preservation
    with open("current_baseline.stim", "r") as f:
        base_circ = stim.Circuit(f.read())
        
    print(f"Baseline circuit loaded. Simulating...")
    
    # To check preservation, we simulate the circuit and check expectations
    sim = stim.TableauSimulator()
    sim.do(base_circ)
    
    preserved = 0
    failed = 0
    for i, s in enumerate(stabs):
        if sim.peek_observable_expectation(s) == 1:
            preserved += 1
        else:
            failed += 1
            # print(f"  Stabilizer {i} NOT preserved.")
            
    print(f"Baseline preserves {preserved}/{len(stabs)} stabilizers.")

if __name__ == "__main__":
    check()
