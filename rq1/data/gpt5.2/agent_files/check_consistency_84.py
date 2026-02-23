import stim

def check_consistency():
    with open("stabilizers_84.txt", "r") as f:
        lines = [line.strip() for line in f if line.strip()]

    stabilizers = []
    for line in lines:
        stabilizers.append(stim.PauliString(line))

    # Try to create a tableau with fewer constraints to see if it works
    # Or just check for contradictions
    try:
        # allow_underconstrained=True handles fewer stabilizers than qubits
        # but does it handle dependent stabilizers?
        # If dependent, they must be consistent.
        tableau = stim.Tableau.from_stabilizers(stabilizers, allow_underconstrained=True, allow_redundant=True)
        print("Tableau creation successful")
    except Exception as e:
        print(f"Tableau creation failed: {e}")

if __name__ == "__main__":
    check_consistency()
