import stim

def check():
    try:
        # Load stabilizers
        with open("target_stabilizers_job.txt", "r") as f:
            lines = [l.strip() for l in f if l.strip()]
        # Handle comma-separated or newline-separated
        if len(lines) == 1 and ',' in lines[0]:
            lines = [x.strip() for x in lines[0].split(',')]
        
        stabs = [stim.PauliString(s) for s in lines]
        print(f"Loaded {len(stabs)} stabilizers.")
        
        # Load candidate
        with open("candidate_split_v2.stim", "r") as f:
            circ = stim.Circuit(f.read())
            
        print(f"Candidate circuit has {circ.num_qubits} qubits.")
        
        # Simulate
        sim = stim.TableauSimulator()
        sim.do(circ)
        
        preserved = 0
        for i, s in enumerate(stabs):
            if sim.peek_observable_expectation(s) == 1:
                preserved += 1
            else:
                if i < 5:
                    print(f"Stabilizer {i} failed: {s}")
                    print(f"Expectation: {sim.peek_observable_expectation(s)}")
        
        print(f"Preserved: {preserved}/{len(stabs)}")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check()
