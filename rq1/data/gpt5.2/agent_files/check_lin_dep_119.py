import stim

def check_dependence():
    with open("stabilizers_119.txt", "r") as f:
        lines = [l.strip() for l in f if l.strip()]
    
    ps = [stim.PauliString(l) for l in lines]
    print(f"Loaded {len(ps)} stabilizers.")
    
    # Gaussian elimination to find rank
    # Use Tableau
    try:
        t = stim.Tableau.from_stabilizers(ps, allow_redundant=True)
        print(f"Tableau created. Number of stabilizers in tableau: {len(t)}")
        # Check if any stabilizers were dropped?
        # stim.Tableau.from_stabilizers returns a Tableau representing the state.
        # It doesn't tell us which were redundant easily, but it succeeds.
        
        # We can convert to a list of destabilizers and stabilizers (x and z outputs).
        # But easier: try to add them one by one.
        
        basis = []
        for i, p in enumerate(ps):
            # Check if p is independent of basis
            # This requires some work.
            pass
            
        # Or just use `len(t)`? No, len(t) is number of qubits.
        print(f"Tableau size (qubits): {len(t)}")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_dependence()
