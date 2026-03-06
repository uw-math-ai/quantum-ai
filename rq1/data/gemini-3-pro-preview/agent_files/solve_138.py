import stim
import sys
import os

def solve():
    filename = r"C:\Users\anpaz\Repos\quantum-ai\rq1\data\gemini-3-pro-preview\agent_files\stabilizers_138.txt"
    with open(filename, 'r') as f:
        lines = [line.strip() for line in f if line.strip()]

    print(f"Loaded {len(lines)} stabilizers.")
    if not lines:
        print("No stabilizers found.")
        return

    # Convert strings to PauliStrings
    try:
        pauli_stabilizers = [stim.PauliString(s) for s in lines]
    except Exception as e:
        print(f"Error parsing stabilizers: {e}")
        return

    # Greedily find a commuting set
    valid_stabilizers = []
    discarded_indices = []
    
    for i, s in enumerate(pauli_stabilizers):
        commutes_with_all = True
        for existing in valid_stabilizers:
            if not s.commutes(existing):
                commutes_with_all = False
                break
        
        if commutes_with_all:
            valid_stabilizers.append(s)
        else:
            discarded_indices.append(i)

    print(f"Kept {len(valid_stabilizers)} stabilizers.")
    print(f"Discarded {len(discarded_indices)} stabilizers at indices: {discarded_indices}")

    # Create tableau
    try:
        # We use from_stabilizers with the filtered list.
        tableau = stim.Tableau.from_stabilizers(valid_stabilizers, allow_redundant=True, allow_underconstrained=True)
    except Exception as e:
        print(f"Error creating tableau: {e}")
        return

    # Convert to circuit
    # method="elimination" is usually robust. "graph_state" is also good.
    circuit = tableau.to_circuit(method="elimination")
    
    output_path = r"C:\Users\anpaz\Repos\quantum-ai\rq1\data\gemini-3-pro-preview\agent_files\circuit_138.stim"
    with open(output_path, "w") as f:
        f.write(str(circuit))
    
    print(f"Circuit generated successfully and saved to {output_path}")

if __name__ == "__main__":
    solve()
