import stim
import sys
import os

def check_stabilizers(filename):
    with open(filename, 'r') as f:
        lines = [line.strip() for line in f if line.strip()]

    print(f"Loaded {len(lines)} stabilizers.")
    
    # Check lengths
    for i, line in enumerate(lines):
        if len(line) != 135:
            print(f"Line {i+1} has length {len(line)}: {line}")
            
    lengths = [len(l) for l in lines]
    if len(set(lengths)) > 1:
        print(f"Error: Inconsistent lengths: {set(lengths)}")
        return
    
    n_qubits = lengths[0]
    print(f"Qubits: {n_qubits}")
    
    # Check for invalid characters
    for i, line in enumerate(lines):
        if not all(c in 'IXYZ' for c in line):
            print(f"Error: Invalid character in line {i+1}: {line}")
            return

    # Check commutativity
    try:
        # Create tableau
        t = stim.Tableau.from_stabilizers([stim.PauliString(s) for s in lines], allow_redundant=True, allow_underconstrained=True)
        print("Tableau creation successful (commuting).")
        print(f"Number of independent stabilizers: {len(t)}")
    except ValueError as e:
        print(f"Tableau creation failed: {e}")
    # Generate circuit
    # The 'elimination' method generates a circuit that prepares the state.
    c = t.to_circuit("elimination")
    
    # Save the circuit to a file
    with open(r"C:\Users\anpaz\Repos\quantum-ai\rq1\data\gemini-3-pro-preview\agent_files\circuit_135.stim", "w") as f:
        f.write(str(c))
    
    print("Circuit generated and saved.")

if __name__ == "__main__":
    check_stabilizers(r"C:\Users\anpaz\Repos\quantum-ai\rq1\data\gemini-3-pro-preview\agent_files\stabilizers_135.txt")
