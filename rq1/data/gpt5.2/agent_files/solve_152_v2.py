import stim
import sys
import os

def solve():
    print("Reading stabilizers...")
    file_path = r"data\gemini-3-pro-preview\agent_files\stabilizers_152.txt"
    with open(file_path, "r") as f:
        stabilizers = [line.strip() for line in f.readlines() if line.strip()]

    print(f"Number of stabilizers: {len(stabilizers)}")
    if not stabilizers:
        print("No stabilizers found.")
        return

    num_qubits = len(stabilizers[0])
    print(f"Number of qubits (length of first stabilizer): {num_qubits}")
    
    # Check consistency of lengths
    for i, s in enumerate(stabilizers):
        if len(s) != num_qubits:
            print(f"Error: Stabilizer {i} has length {len(s)}, expected {num_qubits}")
            return

    print("Generating circuit using stim.Tableau.from_stabilizers...")
    try:
        paulis = [stim.PauliString(s) for s in stabilizers]
        tableau = stim.Tableau.from_stabilizers(paulis, allow_underconstrained=True)
        circuit = tableau.to_circuit("elimination")
        
        print("Circuit generated successfully.")
        print(f"Circuit num_qubits: {circuit.num_qubits}")
        
        output_path = r"data\gemini-3-pro-preview\agent_files\circuit_152_v2.stim"
        with open(output_path, "w") as f:
            f.write(str(circuit))
        print(f"Circuit saved to {output_path}")
        
    except Exception as e:
        print(f"Error generating circuit: {e}")

if __name__ == "__main__":
    solve()
