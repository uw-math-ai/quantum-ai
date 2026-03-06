import stim
import sys

def load_file(filename):
    with open(filename, 'r') as f:
        return f.read().strip()

def load_lines(filename):
    with open(filename, 'r') as f:
        return [line.strip() for line in f if line.strip()]

def verify_local():
    circuit_str = load_file("data/gemini-3-pro-preview/agent_files/circuit_175_generated.stim")
    stabs = load_lines("data/gemini-3-pro-preview/agent_files/stabilizers_current.txt")
    
    circuit = stim.Circuit(circuit_str)
    
    sim = stim.TableauSimulator()
    sim.do(circuit)
    
    # Check each stabilizer
    preserved = 0
    total = len(stabs)
    failed_indices = []
    
    for i, s_str in enumerate(stabs):
        # Check if the expectation value of the stabilizer is +1
        res = sim.peek_observable_expectation(stim.PauliString(s_str))
        if res == 1:
            preserved += 1
        else:
            failed_indices.append(i)
            
    print(f"Preserved {preserved} / {total} stabilizers.")
    if failed_indices:
        print(f"Failed stabilizers: {failed_indices}")

if __name__ == "__main__":
    verify_local()
