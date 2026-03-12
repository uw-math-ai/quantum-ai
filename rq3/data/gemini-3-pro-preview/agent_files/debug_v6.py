import stim
import sys

def check_stabilizers(circuit, stabilizers):
    sim = stim.TableauSimulator()
    sim.do(circuit)
    
    preserved = 0
    total = len(stabilizers)
    
    for s_str in stabilizers:
        try:
            # Strip whitespace
            s_clean = s_str.strip()
            if not s_clean: continue
            p = stim.PauliString(s_clean)
            if sim.peek_observable_expectation(p) == 1:
                preserved += 1
        except Exception as e:
            print(f"Error checking stabilizer '{s_str}': {e}")
            return 0, total
            
    return preserved, total

def main():
    try:
        # Load stabilizers
        with open('target_stabilizers_job.txt', 'r') as f:
            content = f.read()
            # Split by comma
            stabilizers = [s.strip() for s in content.split(',') if s.strip()]

        print(f"Loaded {len(stabilizers)} stabilizers.")

        # Check baseline
        with open('baseline_task.stim', 'r') as f:
            baseline = stim.Circuit(f.read())
        
        pres, total = check_stabilizers(baseline, stabilizers)
        print(f"Baseline: preserved {pres}/{total}")

        # Check candidate
        try:
            with open('candidate_from_stabilizers_v8.stim', 'r') as f:
                candidate = stim.Circuit(f.read())
            pres, total_cand = check_stabilizers(candidate, stabilizers)
            print(f"Candidate: preserved {pres}/{total_cand}")
        except Exception as e:
            print(f"Candidate error: {e}")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
