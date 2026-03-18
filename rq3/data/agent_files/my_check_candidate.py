import stim

def main():
    # Load candidate
    with open("candidate.stim", "r") as f:
        cand_text = f.read()
    cand = stim.Circuit(cand_text)
    
    # Load stabilizers
    stabilizers = []
    with open("target_stabilizers_new.txt", "r") as f:
        for line in f:
            line = line.strip()
            if line:
                stabilizers.append(stim.PauliString(line))
    
    print(f"Checking {len(stabilizers)} stabilizers...")
    
    sim = stim.TableauSimulator()
    sim.do(cand)
    
    failed = 0
    for i, stab in enumerate(stabilizers):
        if not sim.peek_observable_expectation(stab) == 1:
            print(f"Stabilizer {i} failed!")
            failed += 1
            
    if failed == 0:
        print("All stabilizers preserved!")
    else:
        print(f"{failed} stabilizers failed.")

if __name__ == "__main__":
    main()
