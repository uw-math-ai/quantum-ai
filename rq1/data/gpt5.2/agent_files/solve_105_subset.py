import stim
import os

def solve():
    path = r"C:\Users\anpaz\Repos\quantum-ai\rq1\data\gemini-3-pro-preview\agent_files\stabilizers_105_correct.txt"
    if not os.path.exists(path):
        print(f"File not found: {path}")
        return

    with open(path, "r") as f:
        lines = [l.strip() for l in f if l.strip()]

    stabs = [stim.PauliString(l) for l in lines]
    
    # Check consistency
    print(f"Loaded {len(stabs)} stabilizers")
    
    # Simple greedy algorithm for maximal consistent subset
    consistent = []
    dropped_indices = []
    
    for i, s in enumerate(stabs):
        is_comm = True
        for existing in consistent:
            if not s.commutes(existing):
                is_comm = False
                break
        
        if is_comm:
            consistent.append(s)
        else:
            dropped_indices.append(i)
            
    print(f"Kept {len(consistent)} stabilizers.")
    print(f"Dropped {len(dropped_indices)} stabilizers: {dropped_indices}")
    
    if consistent:
        try:
            t = stim.Tableau.from_stabilizers(consistent, allow_redundant=True, allow_underconstrained=True)
            c = t.to_circuit()
            out_path = r"C:\Users\anpaz\Repos\quantum-ai\rq1\data\gemini-3-pro-preview\agent_files\circuit_105_subset.stim"
            with open(out_path, "w") as f:
                f.write(str(c))
            print(f"Circuit generated at {out_path}")
        except Exception as e:
            print(f"Error generating circuit: {e}")

if __name__ == "__main__":
    solve()
