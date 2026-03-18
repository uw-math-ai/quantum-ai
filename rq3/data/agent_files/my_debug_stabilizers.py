import stim

def load_stabilizers(filename):
    with open(filename, "r") as f:
        return [stim.PauliString(line.strip()) for line in f if line.strip()]

targets = load_stabilizers("current_target_stabilizers.txt")

def check_preservation(circuit, targets):
    sim = stim.TableauSimulator()
    sim.do(circuit)
    
    preserved = 0
    total = len(targets)
    
    for stab in targets:
        # peek returns +1, -1, or 0
        exp = sim.peek_observable_expectation(stab)
        if exp == 1:
            preserved += 1
            
    return preserved, total

print("Checking Baseline...")
with open("current_baseline.stim", "r") as f:
    baseline = stim.Circuit(f.read())
p, t = check_preservation(baseline, targets)
print(f"Baseline preserved: {p}/{t}")

print("Checking Graph Candidate...")
with open("candidate_graph_clean.stim", "r") as f:
    cand = stim.Circuit(f.read())
p, t = check_preservation(cand, targets)
print(f"Candidate preserved: {p}/{t}")
