import sys
try:
    import stim
except ImportError:
    print("stim not installed")
    sys.exit(1)

def solve():
    try:
        with open("stabilizers_180.txt", "r") as f:
            lines = [line.strip() for line in f if line.strip()]

        if not lines:
            print("No stabilizers found")
            return

        # Check lengths
        L = len(lines[0])
        print(f"Num stabilizers: {len(lines)}")
        print(f"Qubits: {L}")

        # Parse stabilizers into a Tableau
        # We need to construct a tableau that stabilizes these operators.
        # But we are given generators, not necessarily a full tableau.
        # However, stim.Tableau.from_stabilizers creates a tableau from a set of stabilizers.
        # It assumes we are creating a stabilizer state.
        
        # We need to create a list of PauliStrings
        stabilizers = []
        for line in lines:
            stabilizers.append(stim.PauliString(line))
            
        # Create a tableau from the stabilizers.
        # Stim's from_stabilizers returns a tableau that prepares the state stabilized by the given stabilizers.
        # It requires that the stabilizers are independent and commuting.
        # Also, if there are fewer stabilizers than qubits, the remaining degrees of freedom are arbitrary (logical qubits).
        # We can fill them with Z stabilizers (logical Zs) to fix the state if needed, or stim might handle it.
        # But the problem asks for a circuit that prepares *the* stabilizer state.
        # If the stabilizers don't fully specify the state, then any state stabilized by them is valid.
        
        tableau = stim.Tableau.from_stabilizers(stabilizers, allow_redundant=True, allow_underconstrained=True)
        
        # Convert tableau to circuit
        circuit = tableau.to_circuit()
        
        # Output the circuit to a file
        with open("circuit_180.stim", "w") as f:
            f.write(str(circuit))
            
        print("Circuit generated successfully.")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    solve()
