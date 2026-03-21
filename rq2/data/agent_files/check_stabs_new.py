
import stim
import sys
from inputs_task import circuit_str, stabilizers

def check_stabs():
    circuit = stim.Circuit(circuit_str)
    sim = stim.TableauSimulator()
    sim.do(circuit)
    
    # stabs defined in current_inputs.py
    
    failed = []
    
    for i, s in enumerate(stabilizers):
        s = s.replace(" ", "")
        try:
            ps = stim.PauliString(s)
            expect = sim.peek_observable_expectation(ps)
            if expect != 1:
                failed.append((i, str(ps), expect))
        except Exception as e:
            print(f"Error checking stabilizer {i}: {e}")
            
    print(f"Total stabilizers: {len(stabilizers)}")
    print(f"Failed: {len(failed)}")
    for i, s, e in failed:
        print(f" {i}: {s[:30]}... Expectation: {e}")

if __name__ == "__main__":
    check_stabs()
