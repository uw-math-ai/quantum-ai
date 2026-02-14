import stim
import numpy as np
import sys

def load_stabilizers(filename):
    with open(filename, 'r') as f:
        lines = [l.strip() for l in f if l.strip()]
    return lines

def analyze_stabilizers(stabilizers):
    num_stabs = len(stabilizers)
    if num_stabs == 0:
        print("No stabilizers found.")
        return

    num_qubits = len(stabilizers[0])
    print(f"Number of stabilizers: {num_stabs}")
    print(f"Number of qubits: {num_qubits}")

    # Check for valid characters
    for s in stabilizers:
        if not all(c in 'IXYZ' for c in s):
            print(f"Invalid stabilizer: {s}")
            return

    # Create tableau
    try:
        t = stim.Tableau.from_stabilizers([stim.PauliString(s) for s in stabilizers])
        print("Stabilizers are valid and independent (according to stim)")
    except Exception as e:
        print(f"Error creating tableau: {e}")
        
    # Check commutativity
    print("Checking commutativity...")
    all_commute = True
    for i in range(num_stabs):
        p1 = stim.PauliString(stabilizers[i])
        for j in range(i + 1, num_stabs):
            p2 = stim.PauliString(stabilizers[j])
            if not p1.commutes(p2):
                print(f"Stabilizers {i} and {j} do not commute!")
                all_commute = False
                break
        if not all_commute:
            break
    
    if all_commute:
        print("All stabilizers commute.")

if __name__ == "__main__":
    stabs = load_stabilizers("target_stabilizers_102.txt")
    analyze_stabilizers(stabs)
