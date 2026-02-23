import stim
import sys

def check_commutativity(stabs):
    """Checks if all stabilizers commute pairwise."""
    # Convert string stabilizers to stim.PauliString
    paulis = [stim.PauliString(s) for s in stabs]
    
    n = len(paulis)
    anticommuting_pairs = []
    
    for i in range(n):
        for j in range(i + 1, n):
            if not paulis[i].commutes(paulis[j]):
                anticommuting_pairs.append((i, j))
                
    return anticommuting_pairs

def solve():
    print("Reading stabilizers...")
    with open("my_stabilizers_175_clean.txt", "r") as f:
        stabs = [line.strip() for line in f if line.strip()]

    print(f"Loaded {len(stabs)} stabilizers.")
    
    # Basic validation
    lengths = set(len(s) for s in stabs)
    if len(lengths) > 1:
        print(f"Error: Inconsistent stabilizer lengths: {lengths}")
        for i, s in enumerate(stabs):
            if len(s) != 175:
                print(f"  Stabilizer {i} has length {len(s)}")
                # print(f"  {s}") # Output is too long/truncated often
        
        # Attempt auto-fix by padding with 'I'
        print("Attempting to pad with 'I'...")
        fixed_stabs = []
        max_len = 175 # Force 175
        for s in stabs:
            if len(s) < max_len:
                s = s + "I" * (max_len - len(s))
            fixed_stabs.append(s)
        stabs = fixed_stabs
        print("Fixed stabilizers.")
    
    n_qubits = len(stabs[0])
    print(f"Number of qubits: {n_qubits}")

    # Check commutativity
    print("Checking commutativity...")
    anticommuting = check_commutativity(stabs)
    
    if anticommuting:
        print(f"Found {len(anticommuting)} anticommuting pairs.")
        # If there are anticommuting pairs, we can't satisfy all.
        # We need to find a maximal commuting subset or prioritize.
        # For now, let's just dump the first few pairs to see what's going on.
        for i, j in anticommuting[:10]:
            print(f"  {i} vs {j}:")
            print(f"    {stabs[i]}")
            print(f"    {stabs[j]}")
    else:
        print("All stabilizers commute.")
        import json
        with open("stabilizers_fixed.json", "w") as f:
            json.dump(stabs, f)
        print("Saved fixed stabilizers to stabilizers_fixed.json")

    # Try to generate circuit using stim
    print("Generating circuit...")
    try:
        paulis = [stim.PauliString(s) for s in stabs]
        # Using allow_underconstrained=True to handle cases where we don't specify full N stabilizers
        # But if they anticommute, this might fail or error out.
        tableau = stim.Tableau.from_stabilizers(paulis, allow_underconstrained=True, allow_redundant=True)
        circuit = tableau.to_circuit("elimination")
        
        print("Circuit generated successfully.")
        with open("my_circuit_175.stim", "w") as f:
            f.write(str(circuit))
            
    except Exception as e:
        print(f"Error generating circuit: {e}")

if __name__ == "__main__":
    solve()
