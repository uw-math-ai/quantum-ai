import stim
import numpy as np

stabilizers = [
    "XXXXXXIIIIIIIIIIIIIIIIIIIIIIIIIIIIII",
    "IIIIIIIIIXXXXXXIIIIIIIIIIIIIIIIIIIII",
    "IIIIIIIIIIIIIIIIIIXXXXXXIIIIIIIIIIII",
    "IIIIIIIIIIIIIIIIIIIIIIIIIIIXXXXXXIII",
    "XXXIIIXXXIIIIIIIIIIIIIIIIIIIIIIIIIII",
    "IIIIIIIIIXXXIIIXXXIIIIIIIIIIIIIIIIII",
    "IIIIIIIIIIIIIIIIIIXXXIIIXXXIIIIIIIII",
    "IIIIIIIIIIIIIIIIIIIIIIIIIIIXXXIIIXXX",
    "ZZIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIII",
    "IIIIIIIIIZZIIIIIIIIIIIIIIIIIIIIIIIII",
    "IIIIIIIIIIIIIIIIIIZZIIIIIIIIIIIIIIII",
    "IIIIIIIIIIIIIIIIIIIIIIIIIIIZZIIIIIII",
    "ZIZIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIII",
    "IIIIIIIIIZIZIIIIIIIIIIIIIIIIIIIIIIII",
    "IIIIIIIIIIIIIIIIIIZIZIIIIIIIIIIIIIII",
    "IIIIIIIIIIIIIIIIIIIIIIIIIIIZIZIIIIII",
    "IIIZZIIIIIIIIIIIIIIIIIIIIIIIIIIIIIII",
    "IIIIIIIIIIIIZZIIIIIIIIIIIIIIIIIIIIII",
    "IIIIIIIIIIIIIIIIIIIIIZZIIIIIIIIIIIII",
    "IIIIIIIIIIIIIIIIIIIIIIIIIIIIIIZZIIII",
    "IIIZIZIIIIIIIIIIIIIIIIIIIIIIIIIIIIII",
    "IIIIIIIIIIIIZIZIIIIIIIIIIIIIIIIIIIII",
    "IIIIIIIIIIIIIIIIIIIIIZIZIIIIIIIIIIII",
    "IIIIIIIIIIIIIIIIIIIIIIIIIIIIIIZIZIII",
    "IIIIIIZZIIIIIIIIIIIIIIIIIIIIIIIIIIII",
    "IIIIIIIIIIIIIIIZZIIIIIIIIIIIIIIIIIII",
    "IIIIIIIIIIIIIIIIIIIIIIIIZZIIIIIIIIII",
    "IIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIZZI",
    "IIIIIIZIZIIIIIIIIIIIIIIIIIIIIIIIIIII",
    "IIIIIIIIIIIIIIIZIZIIIIIIIIIIIIIIIIII",
    "IIIIIIIIIIIIIIIIIIIIIIIIZIZIIIIIIIII",
    "IIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIZIZ",
    "XXXIIIIIIXXXIIIIIIXXXIIIIIIXXXIIIIII",
    "ZIIZIIZIIZIIZIIZIIZIIZIIZIIZIIZIIZII"
]

print(f"Num stabilizers: {len(stabilizers)}")
try:
    t = stim.Tableau.from_stabilizers([stim.PauliString(s) for s in stabilizers])
    print(f"Num qubits: {t.num_qubits}")
    print(f"Inverse tableau found.")
    
    # Check if we can create a circuit from it.
    c = t.to_circuit()
    print("Circuit generated successfully from tableau.")
    
except Exception as e:
    print(f"Error: {e}")

# If we have fewer than n stabilizers, we need to complete the set or find a state that satisfies them.
# Let's check for independence.
# We can use Gaussian elimination.

def stabilizers_to_tableau(stabilizers):
    n = len(stabilizers[0])
    num_stab = len(stabilizers)
    tableau = np.zeros((num_stab, 2*n), dtype=int)
    for i, s in enumerate(stabilizers):
        for j, char in enumerate(s):
            if char == 'X':
                tableau[i, j] = 1
            elif char == 'Z':
                tableau[i, j+n] = 1
            elif char == 'Y':
                tableau[i, j] = 1
                tableau[i, j+n] = 1
    return tableau

tab = stabilizers_to_tableau(stabilizers)
# Using stim to do gaussian elimination is easier if we just put them in a Tableau object?
# No, stim.Tableau assumes a full set of n stabilizers.

# Let's just check the rank.
# Or better, let's just try to solve for a circuit.
