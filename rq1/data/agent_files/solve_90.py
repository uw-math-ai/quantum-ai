import stim
import sys

def solve():
    # Read stabilizers
    with open('stabilizers_90.txt', 'r') as f:
        lines = [line.strip() for line in f if line.strip()]

    stabilizers = []
    for line in lines:
        # Remove any trailing punctuation if present (like commas or periods)
        cleaned = line.rstrip(',.')
        stabilizers.append(stim.PauliString(cleaned))

    print(f"Loaded {len(stabilizers)} stabilizers.")

    # Check for commutativity
    for i in range(len(stabilizers)):
        for j in range(i + 1, len(stabilizers)):
            if not stabilizers[i].commutes(stabilizers[j]):
                print(f"Stabilizers {i} and {j} do not commute!")
                return

    # Create tableau
    try:
        tableau = stim.Tableau.from_stabilizers(stabilizers, allow_redundant=True, allow_underconstrained=True)
    except Exception as e:
        print(f"Error creating tableau: {e}")
        # If it fails, maybe because of redundancy or something.
        # But from_stabilizers should handle it if we pass the flags.
        return

    # Convert to circuit
    # The tableau T maps Z bases to the stabilizers.
    # So the circuit for T applied to |0> creates the state.
    circuit = tableau.to_circuit()
    
    with open('circuit_90.stim', 'w') as f:
        f.write(str(circuit))
    
    print("Circuit generated and saved to circuit_90.stim.")

if __name__ == "__main__":
    solve()
