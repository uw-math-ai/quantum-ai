import stim

def verify():
    with open("candidate.stim", "r") as f:
        cand = stim.Circuit(f.read())
        
    with open("stabilizers_task_final.txt", "r") as f:
        stabs = [line.strip() for line in f if line.strip()]
        
    sim = stim.TableauSimulator()
    sim.do_circuit(cand)
    
    preserved = 0
    total = len(stabs)
    
    for s_str in stabs:
        s = stim.PauliString(s_str)
        if sim.peek_observable_expectation(s) == 1:
            preserved += 1
            
    print(f"Candidate preserved {preserved}/{total} stabilizers.")
    
    # Calculate metrics
    cx_count = 0
    volume = 0
    for op in cand:
        if op.name in ['CX', 'CZ']:
            cx_count += len(op.targets_copy()) // 2
        
        if len(op.targets_copy()) > 1:
             volume += len(op.targets_copy())
        else:
             volume += 1
             
    print(f"Candidate 2Q-gate count: {cx_count}")
    print(f"Candidate volume: {volume}")

if __name__ == "__main__":
    verify()
