import stim
import sys

def load_stabilizers(filename):
    with open(filename, 'r') as f:
        stabs = [line.strip() for line in f if line.strip()]
    return stabs

def check_commutativity(stabs):
    paulis = [stim.PauliString(s) for s in stabs]
    n = len(paulis)
    anticommuting = []
    for i in range(n):
        for j in range(i + 1, n):
            if paulis[i].commutes(paulis[j]) == False:
                anticommuting.append((i, j))
    return anticommuting

def solve(filename):
    stabs = load_stabilizers(filename)
    print(f"Loaded {len(stabs)} stabilizers.")
    
    # Basic check for valid chars
    for i, s in enumerate(stabs):
        if not all(c in 'IXYZ' for c in s):
            print(f"Invalid characters in stabilizer {i}: {s}")
            return

    anticommuting = check_commutativity(stabs)
    if anticommuting:
        print(f"Found {len(anticommuting)} anticommuting pairs.")
        # Identify the most problematic stabilizer
        counts = {}
        for i, j in anticommuting:
            counts[i] = counts.get(i, 0) + 1
            counts[j] = counts.get(j, 0) + 1
        
        most_problematic = max(counts, key=counts.get)
        print(f"Most problematic stabilizer is {most_problematic} with {counts[most_problematic]} conflicts.")
        
        # Create a new list without the problematic one
        print(f"Removing stabilizer {most_problematic} and trying again.")
        stabs_new = [s for k, s in enumerate(stabs) if k != most_problematic]
        
        try:
            tableau = stim.Tableau.from_stabilizers([stim.PauliString(s) for s in stabs_new], allow_underconstrained=True, allow_redundant=True)
            circuit = tableau.to_circuit("elimination")
            print("Successfully generated circuit after removing one stabilizer.")
            with open("data/gemini-3-pro-preview/agent_files/circuit_175_generated.stim", "w") as f:
                f.write(str(circuit))
        except Exception as e:
            print(f"Error generating circuit even after removal: {e}")
            return

    else:
        print("All stabilizers commute.")
        try:
            tableau = stim.Tableau.from_stabilizers([stim.PauliString(s) for s in stabs], allow_underconstrained=True, allow_redundant=True)
            circuit = tableau.to_circuit("elimination")
            print("Successfully generated circuit.")
            with open("data/gemini-3-pro-preview/agent_files/circuit_175_generated.stim", "w") as f:
                f.write(str(circuit))
        except Exception as e:
            print(f"Error generating circuit: {e}")
            return

if __name__ == "__main__":
    solve("data/gemini-3-pro-preview/agent_files/stabilizers_current.txt")
