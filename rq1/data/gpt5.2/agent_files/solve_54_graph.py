import stim

def solve():
    with open("stabilizers_54_v2.txt", "r") as f:
        stabilizers = [l.strip() for l in f if l.strip()]

    tableau = stim.Tableau.from_stabilizers(
        [stim.PauliString(s) for s in stabilizers], 
        allow_underconstrained=True
    )
    
    # Try graph_state method
    try:
        circuit = tableau.to_circuit("graph_state")
        with open("circuit_54_graph.stim", "w") as f:
            f.write(str(circuit))
        print(f"Generated circuit_54_graph.stim with {len(circuit)} instructions.")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    solve()
