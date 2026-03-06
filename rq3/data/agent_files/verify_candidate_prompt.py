import stim

def verify_candidate_prompt():
    with open("candidate_prompt.stim", "r") as f:
        cand = stim.Circuit(f.read())
        
    with open("target_stabilizers_prompt.txt", "r") as f:
        lines = [l.strip() for l in f if l.strip()]
        
    print(f"Loaded {len(lines)} stabilizers from prompt file.")
    
    sim = stim.TableauSimulator()
    sim.do(cand)
    
    success = True
    for i, s_str in enumerate(lines):
        try:
            p = stim.PauliString(s_str)
            ev = sim.peek_observable_expectation(p)
            if ev != 1:
                print(f"FAIL: Stabilizer {i} expected +1, got {ev}")
                success = False
                break
        except Exception as e:
            print(f"ERROR on stabilizer {i}: {e}")
            success = False
            break
            
    if success:
        print("SUCCESS: Candidate preserves all prompt stabilizers.")
    else:
        print("FAILURE: Candidate does not preserve prompt stabilizers.")

if __name__ == "__main__":
    verify_candidate_prompt()
