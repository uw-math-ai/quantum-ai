import stim
import sys
import os

# Define path to stabilizers file
STABILIZERS_FILE = r"C:\Users\anpaz\Repos\quantum-ai\rq1\data\gemini-3-pro-preview\agent_files\stabilizers_153.txt"
OUTPUT_FILE = r"C:\Users\anpaz\Repos\quantum-ai\rq1\data\gemini-3-pro-preview\agent_files\circuit_153.stim"

def check_commutativity(stabilizers):
    # Convert to stim.PauliString
    pauli_strings = [stim.PauliString(s) for s in stabilizers]
    
    # Check all pairs
    anticommuting_pairs = []
    for i in range(len(pauli_strings)):
        for j in range(i + 1, len(pauli_strings)):
            if not pauli_strings[i].commutes(pauli_strings[j]):
                anticommuting_pairs.append((i, j))
                
    return anticommuting_pairs

def solve(stabilizers):
    # Convert to stim.PauliString
    pauli_strings = [stim.PauliString(s) for s in stabilizers]
    
    try:
        # allow_underconstrained=True is important if we have fewer than N stabilizers or if they are dependent
        # allow_redundant=True handles linearly dependent stabilizers
        tableau = stim.Tableau.from_stabilizers(pauli_strings, allow_underconstrained=True, allow_redundant=True)
        circuit = tableau.to_circuit("elimination")
        return circuit
    except Exception as e:
        print(f"Error generating circuit: {e}")
        return None

if __name__ == "__main__":
    try:
        if not os.path.exists(STABILIZERS_FILE):
             print(f"File not found: {STABILIZERS_FILE}")
             sys.exit(1)

        with open(STABILIZERS_FILE, "r") as f:
            stabilizers = [line.strip() for line in f if line.strip()]
    except Exception as e:
        print(f"Error reading file: {e}")
        sys.exit(1)
    
    print(f"Loaded {len(stabilizers)} stabilizers.")
    
    anticommuting = check_commutativity(stabilizers)
    if anticommuting:
        print(f"Found {len(anticommuting)} anticommuting pairs.")
        # Only print first few to avoid spam
        for i, j in anticommuting[:5]:
            print(f"  {i} and {j} anticommute")
    else:
        print("All stabilizers commute.")
        
    circuit = solve(stabilizers)
    if circuit:
        print("Successfully generated circuit.")
        with open(OUTPUT_FILE, "w") as f:
            f.write(str(circuit))
            print(f"Circuit written to {OUTPUT_FILE}")
    else:
        print("Failed to generate circuit.")
