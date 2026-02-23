import stim
import os

def solve():
    stab_path = r"C:\Users\anpaz\Repos\quantum-ai\rq1\data\gemini-3-pro-preview\agent_files\stabilizers_60.txt"
    if not os.path.exists(stab_path):
        print(f"File not found: {stab_path}")
        return

    with open(stab_path, "r") as f:
        stabilizers = [line.strip() for line in f if line.strip()]

    print(f"Loaded {len(stabilizers)} stabilizers.")
    for i, s in enumerate(stabilizers):
        if len(s) != 60:
            print(f"Error: Stabilizer {i} has length {len(s)}")
            return

    try:
        t = stim.Tableau.from_stabilizers(
            [stim.PauliString(s) for s in stabilizers], 
            allow_underconstrained=True,
            allow_redundant=True
        )
        circuit = t.to_circuit()
        
        output_path = r"C:\Users\anpaz\Repos\quantum-ai\rq1\data\gemini-3-pro-preview\agent_files\circuit_60.stim"
        with open(output_path, "w") as f:
            f.write(str(circuit))
        print(f"Circuit saved to {output_path}")
        
    except Exception as e:
        print(f"Failed: {e}")

if __name__ == "__main__":
    solve()
