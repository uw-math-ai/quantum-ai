import stim

def solve():
    with open('target_stabilizers_63.txt', 'r') as f:
        lines = [line.strip() for line in f if line.strip()]

    # Create Tableau from stabilizers
    try:
        stabilizers = [stim.PauliString(line) for line in lines]
        t = stim.Tableau.from_stabilizers(stabilizers, allow_underconstrained=True)
        circuit = t.to_circuit(method="elimination")
        print(circuit)
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    solve()
