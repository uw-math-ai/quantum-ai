import stim

def solve_best_effort():
    try:
        with open(r"C:\Users\anpaz\Repos\quantum-ai\rq1\stabilizers_171_new.txt", "r") as f:
            lines = [line.strip() for line in f if line.strip()]
        
        stabs = [stim.PauliString(line) for line in lines]
        
        # Greedy approach: keep adding stabilizers if they commute with all previous ones
        kept = []
        dropped = []
        kept_indices = []
        
        for i, s in enumerate(stabs):
            commutes = True
            for k in kept:
                if not s.commutes(k):
                    commutes = False
                    break
            if commutes:
                kept.append(s)
                kept_indices.append(i)
            else:
                dropped.append(i)
                
        print(f"Kept {len(kept)} stabilizers. Dropped {len(dropped)}")
        print(f"Dropped indices: {dropped}")
        
        # Generate circuit for the kept ones
        tableau = stim.Tableau.from_stabilizers(kept, allow_underconstrained=True)
        circuit = tableau.to_circuit("elimination")
        
        with open(r"C:\Users\anpaz\Repos\quantum-ai\rq1\circuit_171_best.stim", "w") as f:
            f.write(str(circuit))
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    solve_best_effort()
