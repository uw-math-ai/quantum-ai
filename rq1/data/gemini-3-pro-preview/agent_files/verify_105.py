import stim
import sys
import os

def read_stabilizers(filename):
    with open(filename, 'r') as f:
        stabs = [line.strip() for line in f if line.strip()]
    return stabs

def check():
    base_dir = r'C:\Users\anpaz\Repos\quantum-ai\rq1\data\gemini-3-pro-preview\agent_files'
    stabs = read_stabilizers(os.path.join(base_dir, 'stabilizers_105.txt'))
    
    circuit_path = os.path.join(base_dir, 'circuit_105.stim')
    with open(circuit_path, 'r') as f:
        circuit_text = f.read()
        
    try:
        circuit = stim.Circuit(circuit_text)
    except Exception as e:
        print(f"Error parsing circuit: {e}")
        return
    
    # We want to check if the circuit prepares a state stabilized by 'stabs'.
    sim = stim.TableauSimulator()
    sim.do(circuit)
    
    # Check each stabilizer
    preserved = 0
    total = len(stabs)
    results = {}
    
    print(f"Checking {total} stabilizers...")
    for s_str in stabs:
        s = stim.PauliString(s_str)
        expect = sim.peek_observable_expectation(s)
        if expect == 1:
            preserved += 1
            results[s_str] = True
        else:
            results[s_str] = False
            
    print(f"Preserved {preserved}/{total}")
    if preserved == total:
        print("SUCCESS")
    else:
        print("FAILURE")
        failures = [s for s, res in results.items() if not res]
        print(f"First 3 failures: {failures[:3]}")

if __name__ == "__main__":
    check()
