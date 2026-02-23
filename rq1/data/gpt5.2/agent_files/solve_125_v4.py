import stim
import sys

def solve():
    try:
        with open(r'C:\Users\anpaz\Repos\quantum-ai\rq1\data\gemini-3-pro-preview\agent_files\stabilizers_125_new.txt', 'r') as f:
            lines = [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        print("Stabilizer file not found.")
        return

    stabilizers = [stim.PauliString(s) for s in lines]
    
    # Create tableau
    tableau = stim.Tableau.from_stabilizers(
        stabilizers, 
        allow_underconstrained=True, 
        allow_redundant=True
    )
    circuit = tableau.to_circuit("elimination")
    
    # Write to file, iterating over instructions to avoid long line wrapping issues if any
    output_path = r'C:\Users\anpaz\Repos\quantum-ai\rq1\circuit_125_fixed.stim'
    with open(output_path, 'w') as f:
        for instruction in circuit:
            f.write(str(instruction) + "\n")
    
    print(f"Circuit written to {output_path}")

if __name__ == "__main__":
    solve()
