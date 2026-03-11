import stim
import sys

def check(circuit_file, stabilizers_file):
    print(f"Checking {circuit_file}...")
    with open(circuit_file, "r") as f:
        c = stim.Circuit(f.read())
    with open(stabilizers_file, "r") as f:
        stabs = [stim.PauliString(l.strip()) for l in f if l.strip()]
        
    sim = stim.TableauSimulator()
    sim.do_circuit(c)
    
    for i, s in enumerate(stabs[:5]):
        exp = sim.peek_observable_expectation(s)
        print(f"Stabilizer {i}: {s} -> Expectation: {exp}")
        
    # Check if -1
    neg_count = 0
    zero_count = 0
    pos_count = 0
    for s in stabs:
        e = sim.peek_observable_expectation(s)
        if e == 1: pos_count += 1
        elif e == -1: neg_count += 1
        elif e == 0: zero_count += 1
        
    print(f"Stats: +1: {pos_count}, -1: {neg_count}, 0: {zero_count}")

if __name__ == "__main__":
    check("baseline.stim", "stabilizers.txt")

