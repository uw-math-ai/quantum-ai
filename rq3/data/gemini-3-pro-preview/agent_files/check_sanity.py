import stim
import sys

def verify_and_print():
    # Read stabilizers
    with open('target_stabilizers.txt', 'r') as f:
        stabilizers = [line.strip() for line in f if line.strip()]
    
    # Read baseline circuit to verify we preserve stabilizers
    try:
        baseline = stim.Circuit.from_file('baseline.stim')
    except Exception as e:
        print(f"Error reading baseline: {e}")
        return

    # Check if baseline preserves stabilizers (sanity check)
    sim = stim.TableauSimulator()
    sim.do(baseline)
    for stab in stabilizers:
        if not sim.peek_observable_expectation(stim.PauliString(stab)) == 1:
            print(f"Baseline does NOT preserve: {stab}")
            # This is interesting. If baseline doesn't preserve, then my target list might be wrong?
            # Or the prompt stabilizers are correct and I should optimize for THEM.
            # The prompt says "Target stabilizers (must all be preserved)".
            
if __name__ == '__main__':
    verify_and_print()
