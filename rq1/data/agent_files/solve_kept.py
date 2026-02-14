import stim

def solve():
    with open("stabilizers_kept.txt", "r") as f:
        lines = [line.strip() for line in f if line.strip()]

    stabilizers = [stim.PauliString(line) for line in lines]
    
    print(f"Using {len(stabilizers)} stabilizers.")
    
    try:
        # Try with allow_underconstrained=True
        tableau = stim.Tableau.from_stabilizers(stabilizers, allow_underconstrained=True)
        circuit = tableau.to_circuit()
        
        # Save circuit to file
        with open("circuit_kept.stim", "w") as f:
            f.write(str(circuit))
        print("Circuit generated successfully.")
        
    except Exception as e:
        print(f"Error generating tableau: {e}")
        # Fallback if allow_underconstrained is not supported or fails

if __name__ == "__main__":
    solve()
