import stim
import numpy as np

stabilizers = [
    "XXIIXXIIIIIIIIIIIIIIIIIIII",
    "IIIIIIIXXIIXXIIIIIIIIIIIIIII",
    "IIIIIIIIIIIIIIXXIIXXIIIIIIII",
    "IIIIIIIIIIIIIIIIIIIIIXXIIXXI",
    "XIXIXIXIIIIIIIIIIIIIIIIIIIII",
    "IIIIIIIXIXIXIXIIIIIIIIIIIIII",
    "IIIIIIIIIIIIIIXIXIXIXIIIIIII",
    "IIIIIIIIIIIIIIIIIIIIIXIXIXIX",
    "IIIXXXXIIIIIIIIIIIIIIIIIIIII",
    "IIIIIIIIIIXXXXIIIIIIIIIIIIII",
    "IIIIIIIIIIIIIIIIIXXXXIIIIIII",
    "IIIIIIIIIIIIIIIIIIIIIIIIXXXX",
    "ZZIIZZIIIIIIIIIIIIIIIIIIIIII",
    "IIIIIIIZZIIZZIIIIIIIIIIIIIII",
    "IIIIIIIIIIIIIIZZIIZZIIIIIIII",
    "IIIIIIIIIIIIIIIIIIIIIZZIIZZI",
    "ZIZIZIZIIIIIIIIIIIIIIIIIIIII",
    "IIIIIIIZIZIZIZIIIIIIIIIIIIII",
    "IIIIIIIIIIIIIIZIZIZIZIIIIIII",
    "IIIIIIIIIIIIIIIIIIIIIZIZIZIZ",
    "IIIZZZZIIIIIIIIIIIIIIIIIIIII",
    "IIIIIIIIIIZZZZIIIIIIIIIIIIII",
    "IIIIIIIIIIIIIIIIIZZZZIIIIIII",
    "IIIIIIIIIIIIIIIIIIIIIIIIXXXX", # Wait, looking at the user input again.
    "XXXIIIIXXXIIIIXXXIIIIXXXIIII",
    "ZZZIIIIZZZIIIIZZZIIIIZZZIIII"
]

# Correcting list based on prompt
stabilizers = [
    "XXIIXXIIIIIIIIIIIIIIIIIIII",
    "IIIIIIIXXIIXXIIIIIIIIIIIIIII",
    "IIIIIIIIIIIIIIXXIIXXIIIIIIII",
    "IIIIIIIIIIIIIIIIIIIIIXXIIXXI",
    "XIXIXIXIIIIIIIIIIIIIIIIIIIII",
    "IIIIIIIXIXIXIXIIIIIIIIIIIIII",
    "IIIIIIIIIIIIIIXIXIXIXIIIIIII",
    "IIIIIIIIIIIIIIIIIIIIIXIXIXIX",
    "IIIXXXXIIIIIIIIIIIIIIIIIIIII",
    "IIIIIIIIIIXXXXIIIIIIIIIIIIII",
    "IIIIIIIIIIIIIIIIIXXXXIIIIIII",
    "IIIIIIIIIIIIIIIIIIIIIIIIXXXX",
    "ZZIIZZIIIIIIIIIIIIIIIIIIIIII",
    "IIIIIIIZZIIZZIIIIIIIIIIIIIII",
    "IIIIIIIIIIIIIIZZIIZZIIIIIIII",
    "IIIIIIIIIIIIIIIIIIIIIZZIIZZI",
    "ZIZIZIZIIIIIIIIIIIIIIIIIIIII",
    "IIIIIIIZIZIZIZIIIIIIIIIIIIII",
    "IIIIIIIIIIIIIIZIZIZIZIIIIIII",
    "IIIIIIIIIIIIIIIIIIIIIZIZIZIZ",
    "IIIZZZZIIIIIIIIIIIIIIIIIIIII",
    "IIIIIIIIIIZZZZIIIIIIIIIIIIII",
    "IIIIIIIIIIIIIIIIIZZZZIIIIIII",
    "IIIIIIIIIIIIIIIIIIIIIIIIZZZZ",
    "XXXIIIIXXXIIIIXXXIIIIXXXIIII",
    "ZZZIIIIZZZIIIIZZZIIIIZZZIIII"
]

def analyze_stabilizers(stabs):
    n_qubits = len(stabs[0])
    n_stabs = len(stabs)
    print(f"Number of qubits: {n_qubits}")
    print(f"Number of stabilizers: {n_stabs}")
    
    # Check commutativity
    tableau = stim.Tableau.from_stabilizers([stim.PauliString(s) for s in stabs])
    # Stim doesn't easily expose commutativity check of arbitrary list directly in python without creating tableau, 
    # but creating Tableau from stabilizers enforces commutativity.
    # If it fails, the input is invalid (non-commuting).
    print("Stabilizers commute and are valid.")

    # Looking at the structure
    # There are 26 stabilizers for 28 qubits. 
    # So there are 28 - 26 = 2 logical qubits? Or maybe dependent stabilizers?
    
    # Let's check for independence.
    # We can use Gaussian elimination.
    
    # Convert to binary matrix
    # X part: 1 if X or Y
    # Z part: 1 if Z or Y
    
    matrix = []
    for s in stabs:
        row = []
        # X part
        for char in s:
            row.append(1 if char in 'XY' else 0)
        # Z part
        for char in s:
            row.append(1 if char in 'ZY' else 0)
        matrix.append(row)
    
    matrix = np.array(matrix, dtype=int)
    
    # Gaussian elimination to find rank
    def rank_gf2(mat):
        mat = mat.copy()
        rows, cols = mat.shape
        pivot_row = 0
        for col in range(cols):
            if pivot_row >= rows:
                break
            if mat[pivot_row, col] == 0:
                # Find a swap
                swap_row = -1
                for r in range(pivot_row + 1, rows):
                    if mat[r, col] == 1:
                        swap_row = r
                        break
                if swap_row == -1:
                    continue
                mat[[pivot_row, swap_row]] = mat[[swap_row, pivot_row]]
            
            # Eliminate
            for r in range(rows):
                if r != pivot_row and mat[r, col] == 1:
                    mat[r] = (mat[r] + mat[pivot_row]) % 2
            
            pivot_row += 1
        return pivot_row

    r = rank_gf2(matrix)
    print(f"Rank of stabilizer matrix: {r}")
    
    if r < n_stabs:
        print("Stabilizers are dependent.")
    else:
        print("Stabilizers are independent.")

analyze_stabilizers(stabilizers)
