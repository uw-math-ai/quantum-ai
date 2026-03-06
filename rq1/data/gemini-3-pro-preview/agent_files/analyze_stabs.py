import stim
import os

def load_stabilizers(filename):
    with open(filename, 'r') as f:
        lines = [line.strip() for line in f if line.strip()]
    return lines

def check_commutativity(stabilizers):
    # Convert to stim.PauliString
    paulis = [stim.PauliString(s) for s in stabilizers]
    num_stabs = len(paulis)
    
    anticommuting_pairs = []
    for i in range(num_stabs):
        for j in range(i + 1, num_stabs):
            if not paulis[i].commutes(paulis[j]):
                anticommuting_pairs.append((i, j))
                
    return anticommuting_pairs

def main():
    filename = r'C:\Users\anpaz\Repos\quantum-ai\rq1\data\gemini-3-pro-preview\agent_files\stabilizers.txt'
    stabilizers = load_stabilizers(filename)
    
    print(f"Loaded {len(stabilizers)} stabilizers.")
    
    anticommuting = check_commutativity(stabilizers)
    
    if not anticommuting:
        print("All stabilizers commute.")
    else:
        print(f"Found {len(anticommuting)} anticommuting pairs.")
        for i, j in anticommuting[:10]:
            print(f"  {i} and {j} anticommute")
        if len(anticommuting) > 10:
            print("  ...")

    # Check for independent generators
    # Convert to tableau and Gaussian eliminate
    try:
        t = stim.Tableau.from_stabilizers([stim.PauliString(s) for s in stabilizers], allow_redundant=True, allow_underconstrained=True)
        print("Stabilizers are consistent (can form a state).")
        print(f"Number of qubits: {len(stabilizers[0])}")
        print(f"Rank (independent stabilizers): {len(t)}")
    except Exception as e:
        print(f"Error checking consistency: {e}")

if __name__ == "__main__":
    main()
