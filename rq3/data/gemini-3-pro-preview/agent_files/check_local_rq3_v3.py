import stim
import sys

def check_stabilizers(circuit_str, stabilizers_path):
    circuit = stim.Circuit(circuit_str)
    
    with open(stabilizers_path, "r") as f:
        lines = [l.strip() for l in f if l.strip()]
    
    targets = [stim.PauliString(l) for l in lines]
    
    sim = stim.TableauSimulator()
    sim.do(circuit)
    
    preserved = 0
    for t in targets:
        if sim.measure_observable(t) == 1: # +1 eigenvalue means result is 0 (False) ?? Wait.
             # measure_observable returns the measurement result. 
             # If stabilizer is +1, measurement result is 0 (deterministic).
             # If stabilizer is -1, measurement result is 1.
             # Wait, let's double check stim documentation or behavior.
             # Expectation value +1 -> Result 0 (False).
             # Expectation value -1 -> Result 1 (True).
             pass
        # Actually, measure_observable isn't exactly checking expectation +1 without disturbing.
        # But for stabilizers, it should be deterministic.
        # Let's use peek_observable_expectation? No, Stim doesn't have that easily for all.
        # sim.measure_observable(t) performs a measurement.
        # If the state is stabilized by P, P|psi> = |psi>, then measuring P gives +1 (bit 0).
        # So we expect output False/0.
        
        # However, checking expectation is better done by:
        # expectation = sim.peek_observable_expectation(t)
        # if expectation == 1: preserved += 1
        
        if sim.peek_observable_expectation(t) == 1:
            preserved += 1
            
    print(f"Preserved {preserved}/{len(targets)}")
    if preserved == len(targets):
        print("VALID")
    else:
        print("INVALID")

if __name__ == "__main__":
    circuit_text = sys.stdin.read()
    check_stabilizers(circuit_text, "target_stabilizers_rq3_v3.txt")
