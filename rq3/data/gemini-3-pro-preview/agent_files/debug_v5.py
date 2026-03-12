import stim
import sys

def check_stabilizers(circuit, stabilizers):
    sim = stim.TableauSimulator()
    sim.do(circuit)
    
    preserved = 0
    total = len(stabilizers)
    
    for s_str in stabilizers:
        try:
            p = stim.PauliString(s_str)
            if sim.peek_observable_expectation(p) == 1:
                preserved += 1
        except Exception as e:
            print(f"Error checking stabilizer: {e}")
            return 0, total
            
    return preserved, total

def main():
    try:
        # Load stabilizers
        with open('target_stabilizers_job.txt', 'r') as f:
            stabilizers = [line.strip().replace(',', '') for line in f if line.strip()]

        print(f"Loaded {len(stabilizers)} stabilizers.")

        # Check baseline
        with open('baseline_task.stim', 'r') as f:
            baseline = stim.Circuit(f.read())
        
        pres, total = check_stabilizers(baseline, stabilizers)
        print(f"Baseline: preserved {pres}/{total}")

        # Check candidate
        try:
            with open('candidate_graph_v4.stim', 'r') as f:
                candidate = stim.Circuit(f.read())
            pres, total_cand = check_stabilizers(candidate, stabilizers)
            print(f"Candidate: preserved {pres}/{total_cand}")
        except Exception as e:
            print(f"Candidate error: {e}")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
