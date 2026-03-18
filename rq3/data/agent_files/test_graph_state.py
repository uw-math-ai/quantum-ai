import stim

BASELINE_FILE = r"C:\Users\anpaz\Repos\quantum-ai\rq3\current_baseline.stim"
OUTPUT_FILE = r"C:\Users\anpaz\Repos\quantum-ai\rq3\candidate_test.stim"

def solve():
    with open(BASELINE_FILE, "r") as f:
        baseline = stim.Circuit(f.read())
    
    tableau = stim.Tableau.from_circuit(baseline)
    
    # Synthesize with graph_state
    cand = tableau.to_circuit(method="graph_state")
    
    with open(OUTPUT_FILE, "w") as f:
        f.write(str(cand))
        
    print("Generated candidate_test.stim with graph_state (no permutation).")

if __name__ == "__main__":
    solve()
