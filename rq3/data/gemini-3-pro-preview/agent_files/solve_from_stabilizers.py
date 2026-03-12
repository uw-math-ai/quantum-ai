import stim

def solve():
    print("Reading target stabilizers...")
    with open("target_stabilizers.txt", "r") as f:
        lines = [l.strip() for l in f if l.strip()]
        
    stabilizers = [stim.PauliString(l) for l in lines]
    print(f"Loaded {len(stabilizers)} stabilizers.")
    
    print("Synthesizing tableau from stabilizers...")
    try:
        # Try strict first
        tableau = stim.Tableau.from_stabilizers(stabilizers, allow_redundant=True, allow_underconstrained=True)
    except Exception as e:
        print(f"Synthesis failed: {e}")
        return

    print("Synthesizing circuit (graph state)...")
    circuit = tableau.to_circuit(method="graph_state")
    
    print("Cleaning circuit...")
    # Replace RX with H
    clean_circuit = str(circuit).replace("RX", "H")
    
    with open("candidate_from_stabs.stim", "w") as f:
        f.write(clean_circuit)
        
    print("Done.")

if __name__ == "__main__":
    solve()
