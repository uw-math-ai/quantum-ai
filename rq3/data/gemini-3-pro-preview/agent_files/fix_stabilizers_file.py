import stim

def write_stabs():
    with open("current_task_baseline.stim", "r") as f:
        baseline = stim.Circuit(f.read())
    
    sim = stim.TableauSimulator()
    sim.do(baseline)
    stabs = sim.canonical_stabilizers()
    
    # Write to current_task_stabilizers.txt
    with open("current_task_stabilizers.txt", "w") as f:
        for s in stabs:
            f.write(str(s) + "\n")
            
    # Also write to target_stabilizers.txt just in case
    with open("target_stabilizers.txt", "w") as f:
        for s in stabs:
            f.write(str(s) + "\n")
            
    print(f"Wrote {len(stabs)} stabilizers to files.")

write_stabs()
