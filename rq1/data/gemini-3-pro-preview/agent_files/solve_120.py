import stim
import sys
import os

def solve():
    try:
        input_path = r'C:\Users\anpaz\Repos\quantum-ai\rq1\data\gemini-3-pro-preview\agent_files\stabilizers_120.txt'
        output_path = r'C:\Users\anpaz\Repos\quantum-ai\rq1\data\gemini-3-pro-preview\agent_files\circuit_120.stim'
        
        with open(input_path, 'r') as f:
            lines = [l.strip() for l in f if l.strip()]
        
        num_qubits = len(lines[0])
        print(f"Num qubits: {num_qubits}")
        print(f"Num stabilizers: {len(lines)}")
        
        # Convert strings to PauliStrings
        stabilizers = [stim.PauliString(line) for line in lines]
        
        # Check for conflicts
        t = stim.Tableau.from_stabilizers(stabilizers, allow_redundant=True, allow_underconstrained=True)
        
        c = t.to_circuit()
        
        with open(output_path, 'w') as f:
            f.write(str(c))
            
        print("Circuit generated successfully.")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    solve()
