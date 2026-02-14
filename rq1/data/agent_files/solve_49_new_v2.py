import stim

def solve():
    with open("stabilizers_49_v2.txt", "r") as f:
        lines = [l.strip() for l in f if l.strip()]
    
    try:
        # Create tableau from stabilizers
        # allow_underconstrained=True is necessary if < 49 stabilizers
        # using 'elimination' method usually gives simpler circuits for state prep
        tableau = stim.Tableau.from_stabilizers([stim.PauliString(s) for s in lines], allow_underconstrained=True)
        
        # Convert to circuit
        circuit = tableau.to_circuit("elimination")
        
        # Output circuit to stdout so we can capture it
        print(circuit)
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    solve()
