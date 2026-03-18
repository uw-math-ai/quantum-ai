import stim

def verify():
    print("Verifying candidate_v100.stim...")
    
    # Load stabilizers
    with open("target_stabilizers_v100.txt", "r") as f:
        content = f.read().strip()
        stabilizers_str = [s.strip() for s in content.split(',') if s.strip()]
    
    print(f"Loaded {len(stabilizers_str)} stabilizers.")
    
    # Load circuit
    with open("candidate_v100.stim", "r") as f:
        circuit = stim.Circuit(f.read())
        
    # Simulate
    sim = stim.TableauSimulator()
    sim.do(circuit)
    
    # Check expectations
    failed = False
    for i, s_str in enumerate(stabilizers_str):
        p = stim.PauliString(s_str)
        exp = sim.peek_observable_expectation(p)
        if exp != 1:
            print(f"Stabilizer {i} FAILED: expectation {exp}")
            failed = True
            break
            
    if not failed:
        print("All stabilizers preserved (expectation +1).")
    else:
        print("Verification FAILED.")

if __name__ == "__main__":
    verify()
