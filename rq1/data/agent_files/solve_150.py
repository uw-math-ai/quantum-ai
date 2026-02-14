import stim
import os

def load_stabilizers(filename):
    with open(filename, 'r') as f:
        lines = [line.strip() for line in f if line.strip()]
    return lines

def solve():
    stabilizers = load_stabilizers('target_stabilizers_150.txt')
    num_qubits = len(stabilizers[0])
    num_stabilizers = len(stabilizers)
    
    print(f"Loaded {num_stabilizers} stabilizers for {num_qubits} qubits")
    
    # Check if we have 150 stabilizers
    if num_stabilizers != 150:
        print("Warning: Number of stabilizers is not 150")
    
    try:
        t = stim.Tableau.from_stabilizers([stim.PauliString(s) for s in stabilizers], allow_redundant=True, allow_underconstrained=True)
        circuit = t.to_circuit()
        
        print("Circuit generated successfully")
        with open('solve_150_circuit.stim', 'w') as f:
            f.write(str(circuit))
            
    except Exception as e:
        print(f"Error generating circuit: {e}")

if __name__ == "__main__":
    solve()
