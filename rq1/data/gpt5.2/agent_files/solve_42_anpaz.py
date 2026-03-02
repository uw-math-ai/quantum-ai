import stim
import sys

def check_commutativity(stabilizers):
    print("Checking commutativity...")
    paulis = [stim.PauliString(s) for s in stabilizers]
    n = len(paulis)
    bad_pairs = []
    for i in range(n):
        for j in range(i + 1, n):
            if not paulis[i].commutes(paulis[j]):
                bad_pairs.append((i, j))
                if len(bad_pairs) < 5:
                    print(f"Anticommutation detected between index {i} and {j}")
                    print(f"  {stabilizers[i]}")
                    print(f"  {stabilizers[j]}")
    
    if bad_pairs:
        print(f"Total anticommuting pairs: {len(bad_pairs)}")
        return False
    return True

def solve():
    try:
        with open(r"data\gemini-3-pro-preview\agent_files\stabilizers_42.txt", "r") as f:
            stabilizers = [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
         print("Stabilizer file not found")
         return

    print(f"Loaded {len(stabilizers)} stabilizers.")
    
    if not check_commutativity(stabilizers):
        print("Stabilizers do not commute! Cannot form a valid state with simple Tableau.from_stabilizers.")
        return

    try:
        # allow_underconstrained=True is important if we have fewer than N independent stabilizers
        tableau = stim.Tableau.from_stabilizers(
            [stim.PauliString(s) for s in stabilizers], 
            allow_underconstrained=True,
            allow_redundant=True
        )
        circuit = tableau.to_circuit()
        
        print("Circuit generated successfully.")
        
        with open(r"data\gemini-3-pro-preview\agent_files\circuit_42.stim", "w") as f:
            f.write(str(circuit))
        print("Circuit written to data\gemini-3-pro-preview\agent_files\circuit_42.stim")

    except Exception as e:
        print(f"Error creating circuit: {e}")

if __name__ == "__main__":
    solve()

