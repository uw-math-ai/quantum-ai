import stim

def verify_clean_circuit():
    circuit_file = r'C:\Users\anpaz\Repos\quantum-ai\rq1\data\gemini-3-pro-preview\agent_files\circuit_clean.stim'
    stabs_file = r'C:\Users\anpaz\Repos\quantum-ai\rq1\data\gemini-3-pro-preview\agent_files\stabilizers.txt'
    
    with open(circuit_file, 'r') as f:
        circuit_str = f.read()
    
    try:
        circuit = stim.Circuit(circuit_str)
        print("Circuit parsed successfully.")
    except Exception as e:
        print(f"Circuit parsing failed: {e}")
        return

    # Verify
    with open(stabs_file, 'r') as f:
        lines = [line.strip() for line in f if line.strip()]
        
    sim = stim.TableauSimulator()
    sim.do(circuit)
    
    failed = []
    for i, line in enumerate(lines):
        p = stim.PauliString(line)
        expected = sim.peek_observable_expectation(p)
        if expected != 1:
            failed.append((i, expected))
            
    if not failed:
        print("All stabilizers passed verification.")
    else:
        print(f"Failed {len(failed)} stabilizers: {failed}")

if __name__ == "__main__":
    verify_clean_circuit()
