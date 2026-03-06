import stim

def debug_stabilizers():
    with open('target_stabilizers_v2.txt', 'r') as f:
        stabilizers = [line.strip() for line in f if line.strip()]

    print(f"Loaded {len(stabilizers)} stabilizers.")
    
    # Check lengths
    lengths = [len(s) for s in stabilizers]
    print(f"Lengths: {set(lengths)}")
    for i, l in enumerate(lengths):
        if l != 138:
            print(f"Stabilizer {i} has length {l}")
    
    # Check commutativity
    anticommuting_pairs = []
    for i in range(len(stabilizers)):
        for j in range(i + 1, len(stabilizers)):
            p1 = stim.PauliString(stabilizers[i])
            p2 = stim.PauliString(stabilizers[j])
            if not p1.commutes(p2):
                anticommuting_pairs.append((i, j))
                print(f"Stabilizers {i} and {j} anticommute.")
                # print(f"{i}: {stabilizers[i]}")
                # print(f"{j}: {stabilizers[j]}")

    if not anticommuting_pairs:
        print("All stabilizers commute.")
    else:
        print(f"Found {len(anticommuting_pairs)} anticommuting pairs.")

    # Check baseline
    with open('current_baseline_v2.stim', 'r') as f:
        circuit_text = f.read()
    circuit = stim.Circuit(circuit_text)
    
    sim = stim.TableauSimulator()
    sim.do(circuit)
    
    print("\nChecking baseline preservation:")
    for i, stab_str in enumerate(stabilizers):
        try:
            p = stim.PauliString(stab_str)
            if sim.peek_observable_expectation(p) != 1:
                print(f"Baseline fails to preserve stabilizer {i}")
        except Exception as e:
            print(f"Error checking stabilizer {i}: {e}")

if __name__ == "__main__":
    debug_stabilizers()
