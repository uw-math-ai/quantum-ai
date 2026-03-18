import stim
import sys

def main():
    try:
        with open("baseline_attempt_01.stim", "r") as f:
            baseline_text = f.read()
            baseline = stim.Circuit(baseline_text)
        
        with open("target_stabilizers.txt", "r") as f:
            target_lines = [line.strip() for line in f if line.strip()]
            
    except Exception as e:
        print(f"Error loading files: {e}")
        return

    sim = stim.TableauSimulator()
    sim.do(baseline)
    
    preserved = 0
    total = len(target_lines)
    
    for stab_str in target_lines:
        try:
            p = stim.PauliString(stab_str)
            # Expectation +1 means P|psi> = |psi>
            expectation = sim.peek_observable_expectation(p)
            if expectation == 1:
                preserved += 1
            else:
                pass # Not preserved (+1)
        except Exception as e:
            print(f"Error checking stabilizer {stab_str}: {e}")
            
    print(f"Baseline preserves {preserved}/{total} stabilizers.")

if __name__ == "__main__":
    main()
