import stim

def load_stabilizers(filename):
    with open(filename, 'r') as f:
        lines = [line.strip() for line in f if line.strip()]
    return lines

def main():
    circuit_file = r'C:\Users\anpaz\Repos\quantum-ai\rq1\data\gemini-3-pro-preview\agent_files\circuit.stim'
    stabs_file = r'C:\Users\anpaz\Repos\quantum-ai\rq1\data\gemini-3-pro-preview\agent_files\stabilizers.txt'
    
    with open(circuit_file, 'r') as f:
        circuit_str = f.read()
    circuit = stim.Circuit(circuit_str)
    
    stabilizers = load_stabilizers(stabs_file)
    paulis = [stim.PauliString(s) for s in stabilizers]
    
    tableau = stim.Tableau.from_circuit(circuit)
    
    failed = []
    
    # Simulate
    sim = stim.TableauSimulator()
    sim.do(circuit)
    
    # Check each stabilizer
    for i, line in enumerate(stabilizers):
        p = stim.PauliString(line)
        expected = sim.peek_observable_expectation(p)
        if expected != 1:
            failed.append((i, expected))
            
    if not failed:
        print("All stabilizers passed verification.")
    else:
        print(f"Failed {len(failed)} stabilizers: {failed}")

if __name__ == "__main__":
    main()
