import stim

def verify():
    # Load 90 stabilizers
    with open('target_stabilizers_challenge.txt', 'r') as f:
        # Truncate to 92
        all_stabilizers = [stim.PauliString(l.strip()[:92]) for l in f if l.strip()]
    
    # Identify the 89 we expect to preserve (all except index 16)
    expected_preserved = [s for i, s in enumerate(all_stabilizers) if i != 16]
    
    # Load candidate
    with open('candidate.stim', 'r') as f:
        circuit_text = f.read()
    circuit = stim.Circuit(circuit_text)
    
    # Simulate
    sim = stim.TableauSimulator()
    sim.do(circuit)
    
    failed = []
    for i, s in enumerate(expected_preserved):
        if sim.peek_observable_expectation(s) != 1:
            failed.append(i)
            
    if failed:
        print(f"Candidate fails {len(failed)} of the 89 expected stabilizers.")
        print(f"First failure index in subset: {failed[0]}")
    else:
        print("Candidate preserves all 89 expected stabilizers.")

    # Check 16
    s16 = all_stabilizers[16]
    res = sim.peek_observable_expectation(s16)
    print(f"Stabilizer 16 expectation: {res}")

if __name__ == "__main__":
    verify()
