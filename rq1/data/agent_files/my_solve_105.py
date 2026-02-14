import stim
import numpy as np

def solve():
    with open('my_stabilizers_105.txt', 'r') as f:
        stabilizers = [line.strip() for line in f if line.strip()]

    num_stabilizers = len(stabilizers)
    num_qubits = len(stabilizers[0])
    print(f"Loaded {num_stabilizers} stabilizers for {num_qubits} qubits")
    
    # Check if we have a full stabilizer set
    if num_stabilizers != num_qubits:
        print(f"Warning: Number of stabilizers ({num_stabilizers}) != number of qubits ({num_qubits}).")
        # We need to fill the rest with trivial stabilizers if possible, or just generate a state that satisfies these.
        # But Stim's Tableau.from_stabilizers creates a tableau where the first k rows are the given stabilizers.
        # The remaining rows are filled arbitrarily to make it a valid Clifford tableau.
        # This effectively "fixes" the values of the other stabilizers.
        # If we just want ANY state that satisfies the given stabilizers, this is fine.
        
    try:
        t = stim.Tableau.from_stabilizers([stim.PauliString(s) for s in stabilizers], allow_underconstrained=True)
        # This tableau T has the property that T * Z_k * T^-1 = stabilizer_k
        # So stabilizer_k stabilizes T|0>.
        # So we just need to implement T.
        
        circuit = t.to_circuit()
        
        with open('circuit_candidate_105.stim', 'w') as f:
            f.write(str(circuit))
            
        print("Circuit generated successfully.")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    solve()
