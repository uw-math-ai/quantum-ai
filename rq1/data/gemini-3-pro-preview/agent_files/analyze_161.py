import stim
import sys
import os

def load_stabilizers(filename):
    if not os.path.exists(filename):
        print(f"File not found: {filename}")
        return []
    with open(filename, 'r') as f:
        lines = [line.strip() for line in f if line.strip()]
    return lines

def analyze_stabilizers(stabilizers):
    if not stabilizers:
        return
    num_stabilizers = len(stabilizers)
    num_qubits = len(stabilizers[0])
    print(f"Number of stabilizers: {num_stabilizers}")
    print(f"Number of qubits: {num_qubits}")

    # Check lengths
    for i, s in enumerate(stabilizers):
        if len(s) != num_qubits:
            print(f"Error: Stabilizer {i} has length {len(s)}, expected {num_qubits}")
            return

    # Check consistency (commutativity)
    print("\nChecking commutativity...")
    anticommuting_pairs = []
    
    def commutes(s1, s2):
        # 0: I, 1: X, 2: Y, 3: Z
        # Two paulis anticommute if they differ and neither is I.
        # Total anticommutations must be even for commutativity.
        anticomms = 0
        for c1, c2 in zip(s1, s2):
            if c1 == 'I' or c2 == 'I':
                continue
            if c1 != c2:
                anticomms += 1
        return anticomms % 2 == 0

    for i in range(num_stabilizers):
        for j in range(i + 1, num_stabilizers):
            if not commutes(stabilizers[i], stabilizers[j]):
                anticommuting_pairs.append((i, j))
                if len(anticommuting_pairs) < 10:
                     print(f"Stabilizers {i} and {j} anticommute.")
    
    print(f"Total anticommuting pairs: {len(anticommuting_pairs)}")

    if len(anticommuting_pairs) == 0:
        print("All stabilizers commute.")
        try:
             # Try to create a Tableau to verify independence and validity
             t = stim.Tableau.from_stabilizers([stim.PauliString(s) for s in stabilizers])
             print("Successfully created Tableau from stabilizers.")
        except Exception as e:
             print(f"Failed to create Tableau: {e}")
    else:
        print("Stabilizers are inconsistent.")

if __name__ == "__main__":
    stabilizers = load_stabilizers(r"C:\Users\anpaz\Repos\quantum-ai\rq1\data\gemini-3-pro-preview\agent_files\stabs_161.txt")
    analyze_stabilizers(stabilizers)
