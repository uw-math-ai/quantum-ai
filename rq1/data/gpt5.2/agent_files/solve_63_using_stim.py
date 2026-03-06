import stim

def solve():
    with open("data/gemini-3-pro-preview/agent_files/stabilizers_63.txt", "r") as f:
        stabilizers = [l.strip() for l in f.readlines() if l.strip()]

    print(f"Loaded {len(stabilizers)} stabilizers.")

    # Try to generate tableau directly
    try:
        # stim.Tableau.from_stabilizers requires a list of stim.PauliString
        pauli_strings = [stim.PauliString(s) for s in stabilizers]
        
        # Check if we have enough stabilizers.
        # If not, we might need to add one to fix the gauge.
        # Usually adding Z on the logical qubit is safe if we just want "a" state.
        # But let's see what Stim does.
        
        tableau = stim.Tableau.from_stabilizers(pauli_strings, allow_redundant=True, allow_underconstrained=True)
        circuit = tableau.to_circuit()
        
        print("Circuit generated successfully.")
        with open("circuit_generated.stim", "w") as f:
            f.write(str(circuit))
        
    except Exception as e:
        print(f"Error generating tableau: {e}")

if __name__ == "__main__":
    solve()
