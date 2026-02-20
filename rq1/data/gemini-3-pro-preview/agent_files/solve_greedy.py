import stim

# Load stabs
with open(r'data/gemini-3-pro-preview/agent_files/stabs.txt', 'r') as f:
    stabs = [line.strip() for line in f if line.strip()]

# Pad
for i in range(len(stabs)):
    if len(stabs[i]) < 180:
        stabs[i] = stabs[i] + 'I' * (180 - len(stabs[i]))

# Try to find a maximal commuting set
# We prioritize earlier stabilizers? Or just greedy?
# Let's try greedy: keep S_i if it commutes with all already kept stabilizers.

kept_indices = []
kept_paulis = []

print("Selecting commuting subset...")
for i in range(len(stabs)):
    p = stim.PauliString(stabs[i])
    commutes = True
    for kp in kept_paulis:
        if not p.commutes(kp):
            commutes = False
            break
    if commutes:
        kept_indices.append(i)
        kept_paulis.append(p)
    else:
        print(f"Skipping stabilizer {i} due to anticommutation.")

print(f"Kept {len(kept_indices)} out of {len(stabs)} stabilizers.")

# Generate circuit from kept stabilizers
try:
    tableau = stim.Tableau.from_stabilizers(kept_paulis, allow_underconstrained=True, allow_redundant=True)
    circuit = tableau.to_circuit("elimination")
    
    # Verify locally
    sim = stim.TableauSimulator()
    sim.do_circuit(circuit)
    
    satisfied_count = 0
    for i in range(len(stabs)):
        p = stim.PauliString(stabs[i])
        # Measure expectation
        ev = sim.measure_expectation(p)
        if ev == 1:
            satisfied_count += 1
            
    print(f"Satisfied {satisfied_count} out of {len(stabs)} total stabilizers.")
    
    # Save the circuit
    with open(r'data/gemini-3-pro-preview/agent_files/circuit_greedy.stim', 'w') as f:
        f.write(str(circuit))
        
except Exception as e:
    print(f"Error: {e}")
