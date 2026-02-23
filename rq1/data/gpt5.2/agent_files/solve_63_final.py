import stim
import sys
import os

def solve():
    # Read stabilizers
    file_path = "data/gemini-3-pro-preview/agent_files/stabilizers_63.txt"
    if not os.path.exists(file_path):
        print(f"Error: File {file_path} not found.")
        return

    with open(file_path, "r") as f:
        stabs = [line.strip() for line in f if line.strip()]

    print(f"Number of stabilizers: {len(stabs)}")
    
    # Check if we have stabilizers
    if not stabs:
        print("No stabilizers found.")
        return

    # Convert strings to stim.PauliString
    try:
        pauli_stabs = [stim.PauliString(s) for s in stabs]
    except Exception as e:
        print(f"Error parsing stabilizers: {e}")
        return

    # Check commutativity
    anticommuting = False
    for i in range(len(pauli_stabs)):
        for j in range(i + 1, len(pauli_stabs)):
            if not pauli_stabs[i].commutes(pauli_stabs[j]):
                # print(f"Warning: Stabilizers {i} and {j} do not commute!")
                anticommuting = True
    
    if anticommuting:
        print("Stabilizers contain anticommuting pairs.")
    else:
        print("All stabilizers commute.")

    # Create tableau from stabilizers
    try:
        # allow_underconstrained=True because we might have fewer stabilizers than qubits
        tableau = stim.Tableau.from_stabilizers(pauli_stabs, allow_underconstrained=True, allow_redundant=True)
        print("Successfully created Tableau from stabilizers.")
        
        circuit = tableau.to_circuit("elimination")
        print("Generated circuit.")
        
        output_path = "data/gemini-3-pro-preview/agent_files/circuit_63_final.stim"
        with open(output_path, "w") as f:
            f.write(str(circuit))
        print(f"Circuit saved to {output_path}")
        
    except Exception as e:
        print(f"Error generating circuit: {e}")

if __name__ == "__main__":
    solve()
