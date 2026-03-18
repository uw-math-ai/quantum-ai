import stim
import sys

def solve():
    print("Loading candidate_from_stabs.stim...")
    with open("candidate_from_stabs.stim", "r") as f:
        circ_text = f.read()
    circuit = stim.Circuit(circ_text)
    
    print("Loading target_stabilizers.txt...")
    with open("target_stabilizers.txt", "r") as f:
        lines = [l.strip() for l in f if l.strip()]
        
    targets = []
    for l in lines:
        try:
            targets.append(stim.PauliString(l))
        except:
            pass
            
    print(f"Loaded {len(targets)} targets.")
    
    sim = stim.TableauSimulator()
    sim.do(circuit)
    
    failed_count = 0
    for i, t in enumerate(targets):
        exp = sim.peek_observable_expectation(t)
        if exp != 1:
            failed_count += 1
            if failed_count <= 5:
                print(f"Stabilizer {i} failed. Expectation: {exp}")
                
    print(f"Total failed: {failed_count}/{len(targets)}")

if __name__ == "__main__":
    solve()
