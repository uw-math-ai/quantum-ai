import stim

def solve():
    # Read stabilizers
    with open('my_target_stabilizers.txt', 'r') as f:
        lines = [line.strip() for line in f if line.strip()]

    # Create tableau
    try:
        t = stim.Tableau.from_stabilizers(lines, allow_redundant=True, allow_underconstrained=True)
    except Exception as e:
        print(f"Error creating tableau: {e}")
        return

    c = t.to_circuit(method="graph_state")
    print(c)

if __name__ == "__main__":
    solve()
