import stim

def solve():
    with open("my_stabilizers_135.txt", "r") as f:
        lines = [line.strip() for line in f if line.strip()]

    # Filter empty lines
    stabilizers = [line for line in lines if len(line) > 0]
    
    # Create PauliStrings
    paulis = [stim.PauliString(s) for s in stabilizers]
    
    print(f"Loaded {len(paulis)} stabilizers.")
    if len(paulis) > 0:
        print(f"Length of stabilizer 0: {len(paulis[0])}")

    try:
        # Create Tableau from stabilizers
        tableau = stim.Tableau.from_stabilizers(paulis, allow_underconstrained=True, allow_redundant=True)
        
        # Convert to circuit
        circuit = tableau.to_circuit("elimination")
        
        # Write to file
        with open("my_circuit_135.stim", "w") as f:
            f.write(str(circuit))
            
        print("Circuit generated successfully.")
        
    except Exception as e:
        print(f"Error generating circuit: {e}")

if __name__ == "__main__":
    solve()
