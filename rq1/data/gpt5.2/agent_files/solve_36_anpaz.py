import stim
import sys

def solve():
    print("Starting solve...")
    try:
        with open("stabilizers_36_anpaz.txt", "r") as f:
            lines = [l.strip() for l in f if l.strip()]
    except FileNotFoundError:
        print("Error: stabilizers_36_anpaz.txt not found")
        return

    stabilizers = []
    for line in lines:
        try:
            stabilizers.append(stim.PauliString(line))
        except Exception as e:
            print(f"Error parsing line '{line}': {e}")
            return

    print(f"Loaded {len(stabilizers)} stabilizers.")

    # Check for anticommutation
    anticommuting_pairs = []
    for i in range(len(stabilizers)):
        for j in range(i + 1, len(stabilizers)):
            if not stabilizers[i].commutes(stabilizers[j]):
                anticommuting_pairs.append((i, j))
    
    if anticommuting_pairs:
        print(f"Found {len(anticommuting_pairs)} anticommuting pairs:")
        for i, j in anticommuting_pairs[:10]:
            print(f"  {i} vs {j}")
        if len(anticommuting_pairs) > 10:
            print("  ...")
    else:
        print("All stabilizers commute.")

    # Try to generate circuit
    try:
        # allow_underconstrained=True because we have 20 stabilizers for 36 qubits
        tableau = stim.Tableau.from_stabilizers(stabilizers, allow_underconstrained=True)
        circuit = tableau.to_circuit("elimination")
        
        print("Circuit generated successfully.")
        with open("circuit_36_anpaz.stim", "w") as f:
            f.write(str(circuit))
        
    except Exception as e:
        print(f"Error generating circuit: {e}")

if __name__ == "__main__":
    solve()
