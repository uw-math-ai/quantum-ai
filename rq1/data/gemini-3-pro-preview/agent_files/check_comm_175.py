import stim
import sys
import os

def solve():
    # Use absolute path to be safe, or just filename if in cwd
    filename = r'C:\Users\anpaz\Repos\quantum-ai\rq1\stabilizers_175.txt'
    
    if not os.path.exists(filename):
        print(f"File {filename} not found.")
        return

    with open(filename, 'r') as f:
        lines = [line.strip().replace(',', '') for line in f if line.strip()]

    # Basic validation
    if not lines:
        print("No stabilizers found.")
        return

    n_qubits = len(lines[0])
    num_stabilizers = len(lines)
    print(f"N qubits: {n_qubits}")
    print(f"Num stabilizers: {num_stabilizers}")
    
    # Check commutativity
    print("Checking commutativity...")
    try:
        paulis = [stim.PauliString(line) for line in lines]
        
        anticommuting_pairs = []
        for i in range(len(paulis)):
            for j in range(i + 1, len(paulis)):
                if not paulis[i].commutes(paulis[j]):
                    anticommuting_pairs.append((i, j))
                    if len(anticommuting_pairs) > 5:
                        break
            if len(anticommuting_pairs) > 5:
                break
        
        if anticommuting_pairs:
            print(f"Stabilizers anticommute! Found {len(anticommuting_pairs)}+ pairs.")
            print(f"First few: {anticommuting_pairs}")
            return
        else:
            print("All stabilizers commute.")
        
        # If we have 175 stabilizers for 175 qubits, we can use from_stabilizers
        if len(paulis) == n_qubits:
            print("Full set of stabilizers. Generating circuit...")
            try:
                tableau = stim.Tableau.from_stabilizers(paulis)
                circuit = tableau.to_circuit()
                print("Generated circuit from full tableau.")
                with open('circuit_175.stim', 'w') as f:
                    f.write(str(circuit))
            except Exception as e:
                print(f"Error creating tableau: {e}")
        else:
            print(f"Number of stabilizers ({len(paulis)}) != Number of qubits ({n_qubits}). Need to complete the set or use Gaussian elimination.")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    solve()
