
import stim
from current_inputs import CIRCUIT, STABILIZERS

def check():
    c = stim.Circuit(CIRCUIT)
    sim = stim.TableauSimulator()
    sim.do(c)
    
    unsatisfied = []
    for i, s in enumerate(STABILIZERS):
        p = stim.PauliString(s)
        expect = sim.peek_observable_expectation(p)
        if expect != 1:
            unsatisfied.append((i, s, expect))
            
    print(f"Unsatisfied: {len(unsatisfied)}")
    for i, s, obs in unsatisfied:
        print(f"Stabilizer {i}: {s} -> {obs}")

if __name__ == "__main__":
    check()
