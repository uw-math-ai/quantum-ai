import stim
import sys

def check_commutation(stabilizers):
    paulis = [stim.PauliString(s) for s in stabilizers]
    n = len(paulis)
    anticommuting_pairs = []
    for i in range(n):
        for j in range(i + 1, n):
            if paulis[i].commutes(paulis[j]) == False:
                anticommuting_pairs.append((i, j))
    return anticommuting_pairs

def solve():
    with open(r"C:\Users\anpaz\Repos\quantum-ai\rq1\data\gemini-3-pro-preview\agent_files\stabilizers_63.txt", "r") as f:
        stabilizers = [line.strip() for line in f if line.strip()]

    print(f"Loaded {len(stabilizers)} stabilizers.")

    anticommuting = check_commutation(stabilizers)
    if anticommuting:
        print(f"Found {len(anticommuting)} anticommuting pairs.")
        for i, j in anticommuting[:10]:
            print(f"  {i} vs {j}:")
            print(f"    {stabilizers[i]}")
            print(f"    {stabilizers[j]}")
    else:
        print("All stabilizers commute.")

    try:
        tableau = stim.Tableau.from_stabilizers([stim.PauliString(s) for s in stabilizers], allow_underconstrained=True)
        circuit = tableau.to_circuit("elimination")
        print("\nGenerated circuit successfully.")
        with open(r"C:\Users\anpaz\Repos\quantum-ai\rq1\data\gemini-3-pro-preview\agent_files\circuit_63.stim", "w") as f:
            f.write(str(circuit))
        print("Saved circuit to circuit_63.stim")
    except Exception as e:
        print(f"\nFailed to generate circuit: {e}")

if __name__ == "__main__":
    solve()
