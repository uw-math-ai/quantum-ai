import stim

def solve():
    with open("stabilizers_54_v2.txt", "r") as f:
        stabilizers = [l.strip() for l in f if l.strip()]

    tableau = stim.Tableau.from_stabilizers(
        [stim.PauliString(s) for s in stabilizers], 
        allow_underconstrained=True
    )
    
    # Try gaussian method
    circuit = tableau.to_circuit("gaussian")
    
    with open("circuit_54_gaussian.stim", "w") as f:
        f.write(str(circuit))
        
    print(f"Generated circuit_54_gaussian.stim with {len(circuit)} instructions.")

if __name__ == "__main__":
    solve()
