import stim

def solve():
    with open("stabilizers_49.txt", "r") as f:
        lines = [l.strip() for l in f if l.strip()]
    
    print(f"Loaded {len(lines)} stabilizers.")
    
    try:
        # Create tableau from stabilizers
        # allow_underconstrained=True is necessary if < 49 stabilizers
        tableau = stim.Tableau.from_stabilizers([stim.PauliString(s) for s in lines], allow_underconstrained=True)
        
        # Convert to circuit
        circuit = tableau.to_circuit()
        
        # Output circuit to stdout so we can capture it
        print("---CIRCUIT START---")
        print(circuit)
        print("---CIRCUIT END---")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    solve()
