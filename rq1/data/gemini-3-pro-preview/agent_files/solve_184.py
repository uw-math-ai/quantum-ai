import stim
import sys
import os

# Read stabilizers
def read_stabilizers(filename):
    with open(filename, 'r') as f:
        lines = [line.strip().replace(',', '') for line in f if line.strip()]
    return lines

def solve():
    try:
        stabilizers = read_stabilizers('data/gemini-3-pro-preview/agent_files/stabilizers_184.txt')
        
        # Convert strings to stim.PauliString
        stim_stabilizers = [stim.PauliString(s) for s in stabilizers]
        
        # Check if we have enough stabilizers for 184 qubits
        print(f"Number of stabilizers: {len(stim_stabilizers)}")
        print(f"Number of qubits: {len(stim_stabilizers[0])}")

        # Let's try to create a tableau from them directly.
        t = stim.Tableau.from_stabilizers(stim_stabilizers)
        
        # If successful, convert to circuit
        c = t.to_circuit()
        
        print("SUCCESS")
        # print(c) # Don't print the whole circuit yet, it might be large
        
    except Exception as e:
        print("ERROR")
        print(e)

if __name__ == "__main__":
    solve()
