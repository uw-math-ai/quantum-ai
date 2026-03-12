import stim

def check():
    try:
        # Load stabilizers
        with open("target_stabilizers.txt", "r") as f:
            lines = [line.strip() for line in f if line.strip()]
        stabs = []
        for line in lines:
            if line.startswith('+'): line = line[1:]
            line = line.replace('_', 'I')
            stabs.append(stim.PauliString(line))
        
        # Load baseline
        with open("baseline.stim", "r") as f:
            circuit = stim.Circuit(f.read())
            
        print(f"Loaded {len(stabs)} stabilizers and baseline with {circuit.num_qubits} qubits.")
        
        # Check preservation
        sim = stim.TableauSimulator()
        sim.do(circuit)
        
        preserved = 0
        for s in stabs:
            if sim.peek_observable_expectation(s) == 1:
                preserved += 1
                
        print(f"Preserved {preserved}/{len(stabs)} stabilizers.")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check()
