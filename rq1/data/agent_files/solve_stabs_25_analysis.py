import sys
try:
    import stim
    print("stim is available")
except ImportError:
    print("stim is NOT available")

import numpy as np

def char_to_pauli(c):
    if c == 'I': return 0, 0
    if c == 'X': return 1, 0
    if c == 'Z': return 0, 1
    if c == 'Y': return 1, 1
    raise ValueError(f"Invalid char {c}")

stabilizers = [
    "XXIIIXXIIIIIIIIIIIIIIIIII",
    "IIIIIIIIIIXXIIIXXIIIIIIII",
    "IIIIIIXXIIIXXIIIIIIIIIIII",
    "IIIIIIIIIIIIIIIIXXIIIXXII",
    "IIXXIIIXXIIIIIIIIIIIIIIII",
    "IIIIIIIIIIIIXXIIIXXIIIIII",
    "IIIIIIIIXXIIIXXIIIIIIIIII",
    "IIIIIIIIIIIIIIIIIIXXIIIXX",
    "IIIIXIIIIXIIIIIIIIIIIIIII",
    "IIIIIXIIIIXIIIIIIIIIIIIII",
    "IIIIIIIIIIIIIIXIIIIXIIIII",
    "IIIIIIIIIIIIIIIXIIIIXIIII",
    "IIIIIZZIIIZZIIIIIIIIIIIII",
    "IIIIIIIIIIIIIIIZZIIIZZIII",
    "IZZIIIZZIIIIIIIIIIIIIIIII",
    "IIIIIIIIIIIZZIIIZZIIIIIII",
    "IIIIIIIZZIIIZZIIIIIIIIIII",
    "IIIIIIIIIIIIIIIIIZZIIIZZI",
    "IIIZZIIIZZIIIIIIIIIIIIIII",
    "IIIIIIIIIIIIIZZIIIZZIIIII",
    "ZZIIIIIIIIIIIIIIIIIIIIIII",
    "IIIIIIIIIIIIIIIIIIIIIZZII",
    "IIZZIIIIIIIIIIIIIIIIIIIII",
    "IIIIIIIIIIIIIIIIIIIIIIIZZ"
]

n_qubits = 25
n_stabs = len(stabilizers)

print(f"Number of qubits: {n_qubits}")
print(f"Number of stabilizers: {n_stabs}")

# Check if stabilizers commute
def check_commutativity(stabs):
    matrix = []
    for s in stabs:
        row = []
        for char in s:
            x, z = char_to_pauli(char)
            row.extend([x, z])
        matrix.append(row)
    
    matrix = np.array(matrix, dtype=int)
    n = len(stabs[0])
    commute = True
    for i in range(len(stabs)):
        for j in range(i + 1, len(stabs)):
            # Symplectic product
            # For each qubit k, (x1*z2 + z1*x2) % 2
            prod = 0
            for k in range(n):
                x1 = matrix[i, 2*k]
                z1 = matrix[i, 2*k+1]
                x2 = matrix[j, 2*k]
                z2 = matrix[j, 2*k+1]
                prod += (x1 * z2 + z1 * x2)
            if prod % 2 != 0:
                print(f"Stabilizers {i} and {j} do not commute!")
                commute = False
    return commute

if check_commutativity(stabilizers):
    print("All stabilizers commute.")
else:
    print("Stabilizers do NOT commute.")

# If stim is available, use it to find the circuit
if 'stim' in sys.modules:
    tableau = stim.Tableau.from_stabilizers([stim.PauliString(s) for s in stabilizers])
    # However, from_stabilizers requires a full set of n stabilizers for an n-qubit state usually?
    # Or maybe it can handle n-k stabilizers?
    # If not full rank, we might need to complete it.
    
    # Let's try to just use Tableau.from_stabilizers if possible, but 
    # it might expect a list of PauliStrings that fully define the state or just a list.
    # stim.Tableau.from_stabilizers creates a tableau from a list of stabilizers.
    # If the list is incomplete, the remaining generators are arbitrary (usually Z).
    
    # Actually, stim.Tableau.from_stabilizers creates a Tableau that has these stabilizers.
    # But checking the docs, it might interpret the input as the stabilizers of the state.
    # Let's check if we can get a circuit from it.
    pass
