import stim
import sys

def solve():
    try:
        with open(r'C:\Users\anpaz\Repos\quantum-ai\rq1\data\gemini-3-pro-preview\agent_files\my_stabilizers_72.txt', 'r') as f:
            stabilizers = [line.strip() for line in f if line.strip()]
        
        # Check for anticommutativity
        # This is optional but good for debugging if from_stabilizers fails
        
        tableau = stim.Tableau.from_stabilizers([stim.PauliString(s) for s in stabilizers], allow_underconstrained=True)
        circuit = tableau.to_circuit()
        with open(r'C:\Users\anpaz\Repos\quantum-ai\rq1\data\gemini-3-pro-preview\agent_files\circuit_72.stim', 'w') as f:
            print(circuit, file=f)
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    solve()
