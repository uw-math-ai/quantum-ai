import stim

def solve():
    with open("baseline.stim", "r") as f:
        baseline_text = f.read()
    circuit = stim.Circuit(baseline_text)
    
    # Read target stabilizers from the prompt (I'll just paste them here or read from a file)
    # I'll create a file with stabilizers first.
    with open("target_stabilizers.txt", "r") as f:
        lines = f.readlines()
    
    targets = []
    for line in lines:
        line = line.strip()
        if line:
            targets.append(stim.PauliString(line))
            
    print(f"Loaded {len(targets)} target stabilizers.")
    
    sim = stim.TableauSimulator()
    sim.do(circuit)
    
    preserved = 0
    for t in targets:
        if sim.peek_observable_expectation(t) == 1:
            preserved += 1
            
    print(f"Baseline preserves {preserved}/{len(targets)} stabilizers.")

if __name__ == "__main__":
    solve()
