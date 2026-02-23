
import stim

def verify():
    # Read stabilizers
    with open(r'C:\Users\anpaz\Repos\quantum-ai\rq1\data\gemini-3-pro-preview\agent_files\stabilizers_161.txt', 'r') as f:
        stabilizers = [line.strip() for line in f if line.strip()]

    # Read circuit
    with open(r'C:\Users\anpaz\Repos\quantum-ai\rq1\data\gemini-3-pro-preview\agent_files\circuit_161_v2.stim', 'r') as f:
        circuit_text = f.read()

    circuit = stim.Circuit(circuit_text)
    print(f"Circuit qubits: {circuit.num_qubits}")
    print(f"Stabilizer length: {len(stabilizers[0])}")
    
    # We use TableauSimulator because it's efficient for Clifford circuits
    sim = stim.TableauSimulator()
    sim.do(circuit)
    
    preserved_count = 0
    total_count = len(stabilizers)
    
    print(f"Checking {total_count} stabilizers...")
    
    for i, s_str in enumerate(stabilizers):
        s = stim.PauliString(s_str)
        
        # peek_observable returns the expectation value.
        # +1, -1, or 0 (if random).
        
        val = sim.peek_observable_expectation(s)
        
        # Debugging output for first few
        if i < 5:
            print(f"Stabilizer {i}: val={val}")
        
        if val == 1:
            preserved_count += 1
        else:
            # print(f"Stabilizer {i} failed: val={val}")
            pass
            
    print(f"Preserved: {preserved_count}/{total_count}")
    
    if preserved_count == total_count:
        print("SUCCESS: All stabilizers preserved.")
    else:
        print("FAILURE: Some stabilizers not preserved.")

if __name__ == "__main__":
    verify()
