import stim
import sys

def analyze():
    with open(r"C:\Users\anpaz\Repos\quantum-ai\rq1\data\gemini-3-pro-preview\agent_files\stabilizers_56.txt", "r") as f:
        lines = [l.strip() for l in f if l.strip()]

    print(f"Loaded {len(lines)} stabilizers.")
    
    # Check length
    for i, line in enumerate(lines):
        if len(line) != 56:
            print(f"Line {i} has length {len(line)}, expected 56.")
            return

    # Check commutativity
    paulis = [stim.PauliString(line) for line in lines]
    anticommuting_pairs = []
    for i in range(len(paulis)):
        for j in range(i + 1, len(paulis)):
            if not paulis[i].commutes(paulis[j]):
                anticommuting_pairs.append((i, j))
                if len(anticommuting_pairs) < 10:
                    print(f"Anticommute: {i} and {j}")

    if anticommuting_pairs:
        print(f"Total anticommuting pairs: {len(anticommuting_pairs)}")
    else:
        print("All stabilizers commute.")

    # Check independence (rank)
    # We can check this by forming a tableau or using Gaussian elimination logic (simulated)
    # But stim.Tableau.from_stabilizers handles checks too.
    
    if not anticommuting_pairs:
        try:
            t = stim.Tableau.from_stabilizers(paulis, allow_underconstrained=True)
            print("Successfully created Tableau from stabilizers.")
            print(f"Tableau inverse: {t.inverse()}")
        except Exception as e:
            print(f"Failed to create tableau: {e}")

if __name__ == "__main__":
    analyze()
