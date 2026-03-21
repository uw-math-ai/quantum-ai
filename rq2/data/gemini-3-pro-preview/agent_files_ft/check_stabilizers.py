import stim

# Read stabilizers
with open(r"C:\Users\anpaz\Repos\quantum-ai\rq2\data\gemini-3-pro-preview\agent_files_ft\stabilizers.txt", "r") as f:
    stabilizers = [stim.PauliString(l.strip()) for l in f if l.strip()]

# Read circuit
with open(r"C:\Users\anpaz\Repos\quantum-ai\rq2\data\gemini-3-pro-preview\agent_files_ft\baseline.stim", "r") as f:
    circuit = stim.Circuit(f.read())

print(f"Circuit length: {len(circuit)}")

# Simulate
sim = stim.TableauSimulator()
sim.do(circuit)

# Check stabilizers
preserved = 0
for i, s in enumerate(stabilizers):
    # check if s is a stabilizer of the current state
    # method: measure s. If result is deterministic false (0), then it's +1 eigenstate.
    # Note: measure_observable returns True/False. False means +1 eigenvalue for Z-basis?
    # Wait, expectation value:
    # If <psi| P |psi> = +1, then measuring P gives 0 (eigenvalue +1) consistently.
    # If <psi| P |psi> = -1, then measuring P gives 1 (eigenvalue -1) consistently.
    # If 0, then random.
    
    # We can use peek_observable_expectation
    ev = sim.peek_observable_expectation(s)
    if ev == 1:
        preserved += 1
    elif ev == -1:
        print(f"Stabilizer {i} is -1 (anti-stabilized)")
    else:
        print(f"Stabilizer {i} is 0 (random/not stabilized)")

print(f"Preserved stabilizers: {preserved}/{len(stabilizers)}")
