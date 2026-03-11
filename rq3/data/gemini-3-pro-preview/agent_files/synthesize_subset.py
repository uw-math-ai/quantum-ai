
import stim

def solve():
    # Read stabilizers
    with open("C:/Users/anpaz/Repos/quantum-ai/rq3/data/gemini-3-pro-preview/agent_files/target_stabilizers.txt", "r") as f:
        lines = [l.strip() for l in f if l.strip()]

    # Remove index 96 (0-based)
    # Be careful with indices. The error said stabilizers[96].
    # Let's verify the index.
    
    # Check consistency of the rest
    subset = [lines[i] for i in range(len(lines)) if i != 96]
    
    try:
        t = stim.Tableau.from_stabilizers([stim.PauliString(s) for s in subset], allow_underconstrained=True)
        print("Tableau created with 96 removed.")
        
        c = t.to_circuit(method="graph_state")
        print(f"Synthesized circuit with {len(c)} instructions.")
        
        with open("C:/Users/anpaz/Repos/quantum-ai/rq3/data/gemini-3-pro-preview/agent_files/candidate_subset.stim", "w") as f:
            f.write(str(c))
            
    except Exception as e:
        print(f"Still inconsistent: {e}")

solve()
