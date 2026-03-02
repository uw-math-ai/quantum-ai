import stim

def verify_circuit():
    with open("circuit_119.stim", "r") as f:
        circ = stim.Circuit(f.read())
        
    with open("stabilizers_119.txt", "r") as f:
        lines = [l.strip() for l in f if l.strip()]
    
    ps = [stim.PauliString(l) for l in lines]
    
    sim = stim.TableauSimulator()
    sim.do(circ)
    
    # Check index 7
    idx = 7 # 0-based index
    stab = ps[idx]
    print(f"Checking stabilizer {idx}: {lines[idx]}")
    val = sim.peek_observable_expectation(stab)
    print(f"Expectation: {val}")
    
    # Check index 21
    idx = 21
    stab = ps[idx]
    print(f"Checking stabilizer {idx}: {lines[idx]}")
    val = sim.peek_observable_expectation(stab)
    print(f"Expectation: {val}")

if __name__ == "__main__":
    verify_circuit()
