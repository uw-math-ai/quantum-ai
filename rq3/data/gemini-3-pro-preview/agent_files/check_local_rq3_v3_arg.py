import stim
import sys

def check_stabilizers(circuit_path, stabilizers_path):
    with open(circuit_path, "r") as f:
        circuit_str = f.read()
    circuit = stim.Circuit(circuit_str)
    
    with open(stabilizers_path, "r") as f:
        lines = [l.strip() for l in f if l.strip()]
    
    # Pad stabilizers if needed
    # The circuit might have more qubits than stabilizers imply if padded
    # But usually stabilizers define the system size.
    # We should match the length used in generation.
    max_len = max(len(l) for l in lines)
    padded_lines = []
    for l in lines:
        if len(l) < max_len:
            l = l + "I" * (max_len - len(l))
        padded_lines.append(l)
            
    targets = [stim.PauliString(l) for l in padded_lines]
    
    print(f"Checking {len(targets)} stabilizers...")
    sim = stim.TableauSimulator()
    sim.do(circuit)
    
    preserved = 0
    for i, t in enumerate(targets):
        if sim.peek_observable_expectation(t) == 1:
            preserved += 1
        else:
            # Check if it's -1 or 0 (uncertain)
            exp = sim.peek_observable_expectation(t)
            # print(f"Stabilizer {i} failed: {t}, expectation={exp}")
            
    print(f"Preserved {preserved}/{len(targets)}")
    if preserved == len(targets):
        print("VALID")
    else:
        print("INVALID")

if __name__ == "__main__":
    check_stabilizers(sys.argv[1], "target_stabilizers_rq3_v3.txt")
