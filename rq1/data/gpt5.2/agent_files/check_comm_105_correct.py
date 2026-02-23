import stim
import os

def check_comm():
    path = r"C:\Users\anpaz\Repos\quantum-ai\rq1\data\gemini-3-pro-preview\agent_files\stabilizers_105_correct.txt"
    if not os.path.exists(path):
        print(f"File not found: {path}")
        return

    with open(path, "r") as f:
        lines = [l.strip() for l in f if l.strip()]

    print(f"Loaded {len(lines)} stabilizers")
    
    stabs = [stim.PauliString(l) for l in lines]
    
    inconsistent_count = 0
    for i in range(len(stabs)):
        for j in range(i + 1, len(stabs)):
            if not stabs[i].commutes(stabs[j]):
                print(f"Conflict: {i} vs {j}")
                #print(f"  {i}: {lines[i]}")
                #print(f"  {j}: {lines[j]}")
                inconsistent_count += 1
                if inconsistent_count > 10:
                    print("Too many conflicts, stopping output.")
                    return
    
    if inconsistent_count == 0:
        print("All stabilizers commute.")
        
        # Try to generate circuit
        try:
            t = stim.Tableau.from_stabilizers(stabs, allow_redundant=True, allow_underconstrained=True)
            c = t.to_circuit()
            out_path = r"C:\Users\anpaz\Repos\quantum-ai\rq1\data\gemini-3-pro-preview\agent_files\circuit_105_gen.stim"
            with open(out_path, "w") as f:
                f.write(str(c))
            print(f"Circuit generated at {out_path}")
        except Exception as e:
            print(f"Error generating circuit: {e}")

if __name__ == "__main__":
    check_comm()
