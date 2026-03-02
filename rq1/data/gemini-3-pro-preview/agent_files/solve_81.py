import stim
import sys

def solve():
    try:
        with open(r'C:\Users\anpaz\Repos\quantum-ai\rq1\data\gemini-3-pro-preview\agent_files\stabilizers_81_qubits.txt', 'r') as f:
            stabilizers = [line.strip() for line in f if line.strip()]

        print(f"Loaded {len(stabilizers)} stabilizers.")
        
        # Create a tableau from the stabilizers
        # allow_underconstrained=True because we might have fewer than 81 stabilizers for 81 qubits
        # or they might be redundant.
        tableau = stim.Tableau.from_stabilizers(
            [stim.PauliString(s) for s in stabilizers], 
            allow_underconstrained=True,
            allow_redundant=True
        )
        
        print(f"Tableau created. Num qubits: {len(tableau)}")
        
        # Convert to circuit using elimination method (Gaussian elimination)
        circuit = tableau.to_circuit("elimination")
        
        with open(r'C:\Users\anpaz\Repos\quantum-ai\rq1\data\gemini-3-pro-preview\agent_files\circuit_81_qubits.stim', 'w') as f:
            f.write(str(circuit))
            
        print("Circuit generated successfully.")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    solve()
