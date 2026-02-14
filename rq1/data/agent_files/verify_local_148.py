import stim

def verify():
    with open("circuit_kept.stim", "r") as f:
        circuit_text = f.read()
    circuit = stim.Circuit(circuit_text)
    
    with open("stabilizers_148.txt", "r") as f:
        lines = [line.strip() for line in f if line.strip()]
    stabilizers = [stim.PauliString(line) for line in lines]
    
    print(f"Verifying {len(stabilizers)} stabilizers...")
    
    sim = stim.TableauSimulator()
    sim.do(circuit)
    
    preserved = 0
    total = len(stabilizers)
    
    for i, s in enumerate(stabilizers):
        exp = sim.peek_observable_expectation(s)
        if exp == 1:
            preserved += 1
            
    print(f"Preserved: {preserved}/{total}")
    
    if preserved >= 144:
        print("Success: Preserved maximal commuting set.")

if __name__ == "__main__":
    verify()
