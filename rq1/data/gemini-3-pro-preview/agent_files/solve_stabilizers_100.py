import stim
import sys
import os

def solve():
    try:
        # Use absolute path for reading stabilizers
        input_path = r'C:\Users\anpaz\Repos\quantum-ai\rq1\data\gemini-3-pro-preview\agent_files\stabilizers_100.txt'
        with open(input_path, 'r') as f:
            lines = [line.strip() for line in f if line.strip()]

        print(f"Read {len(lines)} stabilizers.")
        if not lines:
            print("No stabilizers found.")
            return

        # Check lengths
        L = len(lines[0])
        print(f"Stabilizer length: {L}")
        for i, line in enumerate(lines):
            if len(line) != L:
                print(f"Error: Stabilizer {i} has length {len(line)}, expected {L}")
                return

        # Create Tableau
        # allow_redundant=True: allows linearly dependent stabilizers (if consistent)
        # allow_underconstrained=True: allows fewer stabilizers than qubits
        try:
            pauli_stabilizers = [stim.PauliString(s) for s in lines]
            tableau = stim.Tableau.from_stabilizers(pauli_stabilizers, allow_redundant=True, allow_underconstrained=True)
            print("Successfully created tableau from stabilizers.")
        except Exception as e:
            print(f"Error creating tableau: {e}")
            # Identify which stabilizers are causing issues if possible
            # e.g. check for anticommutation
            check_anticommutation(lines)
            return

        # Convert to circuit
        circuit = tableau.to_circuit()
        print("Generated circuit.")
        
        # Output the circuit to a file - use absolute path
        output_path = r'C:\Users\anpaz\Repos\quantum-ai\rq1\data\gemini-3-pro-preview\agent_files\circuit_100.stim'
        with open(output_path, 'w') as f:
            f.write(str(circuit))
        print(f"Circuit written to {output_path}")
            
    except Exception as e:
        print(f"An error occurred: {e}")

def check_anticommutation(stabilizers):
    print("Checking for anticommutation...")
    paulis = [stim.PauliString(s) for s in stabilizers]
    for i in range(len(paulis)):
        for j in range(i + 1, len(paulis)):
            if not paulis[i].commutes(paulis[j]):
                print(f"Anticommutation detected between index {i} and {j}")
                print(f"{i}: {stabilizers[i]}")
                print(f"{j}: {stabilizers[j]}")
                return

if __name__ == "__main__":
    solve()
