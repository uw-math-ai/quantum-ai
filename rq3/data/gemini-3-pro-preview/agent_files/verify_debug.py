import stim

# Load stabilizers
with open("target_stabilizers.txt") as f:
    stabilizers = [line.strip() for line in f if line.strip()]

# Load baseline
with open("baseline.stim") as f:
    baseline = stim.Circuit(f.read())

# Load candidate
with open("candidate_graph_baseline.stim") as f:
    candidate = stim.Circuit(f.read())

print(f"Loaded {len(stabilizers)} stabilizers.")

sim = stim.TableauSimulator()
sim.do(baseline)
preserved_base = 0
for s in stabilizers:
    p = stim.PauliString(s)
    if sim.peek_observable_expectation(p) == 1:
        preserved_base += 1
print(f"Baseline preserves {preserved_base}/{len(stabilizers)}")

sim_cand = stim.TableauSimulator()
sim_cand.do(candidate)
preserved_cand = 0
for s in stabilizers:
    p = stim.PauliString(s)
    if sim_cand.peek_observable_expectation(p) == 1:
        preserved_cand += 1
print(f"Candidate preserves {preserved_cand}/{len(stabilizers)}")
