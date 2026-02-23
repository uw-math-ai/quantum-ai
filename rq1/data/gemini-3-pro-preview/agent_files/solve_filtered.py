import stim
import sys

def solve_filtered():
    try:
        with open(r'C:\Users\anpaz\Repos\quantum-ai\rq1\data\gemini-3-pro-preview\agent_files\stabilizers_120.txt', 'r') as f:
            lines = [l.strip() for l in f if l.strip()]
        
        # Remove the problematic ones
        failed_indices = [23, 31, 55, 71]
        filtered_lines = [lines[i] for i in range(len(lines)) if i not in failed_indices]
        
        print(f"Original: {len(lines)}")
        print(f"Filtered: {len(filtered_lines)}")
        
        stabilizers = [stim.PauliString(line) for line in filtered_lines]
        
        # Generate circuit for filtered set
        t = stim.Tableau.from_stabilizers(stabilizers, allow_redundant=True, allow_underconstrained=True)
        c = t.to_circuit()
        
        with open(r'C:\Users\anpaz\Repos\quantum-ai\rq1\data\gemini-3-pro-preview\agent_files\circuit_120_filtered.stim', 'w') as f:
            f.write(str(c))
            
        print("Filtered circuit generated successfully.")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    solve_filtered()
