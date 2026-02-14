import stim
import numpy as np

stabilizers = [
    "XXXXIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIII",
    "IIIIIIIXXXXIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIII",
    "IIIIIIIIIIIIIIXXXXIIIIIIIIIIIIIIIIIIIIIIIIIIIIIII",
    "IIIIIIIIIIIIIIIIIIIIIXXXXIIIIIIIIIIIIIIIIIIIIIIII",
    "IIIIIIIIIIIIIIIIIIIIIIIIIIIIXXXXIIIIIIIIIIIIIIIII",
    "IIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIXXXXIIIIIIIIII",
    "IIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIXXXXIII",
    "XIXIXIXIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIII",
    "IIIIIIIXIXIXIXIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIII",
    "IIIIIIIIIIIIIIXIXIXIXIIIIIIIIIIIIIIIIIIIIIIIIIIII",
    "IIIIIIIIIIIIIIIIIIIIIXIXIXIXIIIIIIIIIIIIIIIIIIIII",
    "IIIIIIIIIIIIIIIIIIIIIIIIIIIIXIXIXIXIIIIIIIIIIIIII",
    "IIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIXIXIXIXIIIIIII",
    "IIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIXIXIXIX",
    "IIXXXXIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIII",
    "IIIIIIIIIXXXXIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIII",
    "IIIIIIIIIIIIIIIIXXXXIIIIIIIIIIIIIIIIIIIIIIIIIIIII",
    "IIIIIIIIIIIIIIIIIIIIIIIXXXXIIIIIIIIIIIIIIIIIIIIII",
    "IIIIIIIIIIIIIIIIIIIIIIIIIIIIIIXXXXIIIIIIIIIIIIIII",
    "IIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIXXXXIIIIIIII",
    "IIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIXXXXI",
    "ZZZZIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIII",
    "IIIIIIIZZZZIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIII",
    "IIIIIIIIIIIIIIZZZZIIIIIIIIIIIIIIIIIIIIIIIIIIIIIII",
    "IIIIIIIIIIIIIIIIIIIIIZZZZIIIIIIIIIIIIIIIIIIIIIIII",
    "IIIIIIIIIIIIIIIIIIIIIIIIIIIIZZZZIIIIIIIIIIIIIIIII",
    "IIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIZZZZIIIIIIIIII",
    "IIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIZZZZIII",
    "ZIZIZIZIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIII",
    "IIIIIIIZIZIZIZIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIII",
    "IIIIIIIIIIIIIIZIZIZIZIIIIIIIIIIIIIIIIIIIIIIIIIIII",
    "IIIIIIIIIIIIIIIIIIIIIZIZIZIZIIIIIIIIIIIIIIIIIIIII",
    "IIIIIIIIIIIIIIIIIIIIIIIIIIIIZIZIZIZIIIIIIIIIIIIII",
    "IIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIZIZIZIZIIIIIII",
    "IIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIZIZIZIZ",
    "IIZZZZIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIII",
    "IIIIIIIIIZZZZIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIII",
    "IIIIIIIIIIIIIIIIZZZZIIIIIIIIIIIIIIIIIIIIIIIIIIIII",
    "IIIIIIIIIIIIIIIIIIIIIIIZZZZIIIIIIIIIIIIIIIIIIIIII",
    "IIIIIIIIIIIIIIIIIIIIIIIIIIIIIIZZZZIIIIIIIIIIIIIII",
    "IIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIZZZZIIIIIIII",
    "IIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIZZZZI",
    "IXXIXIIIXXIXIIIXXIXIIIXXIXIIIIIIIIIIIIIIIIIIIIIII",
    "IXXIXIIIIIIIIIIXXIXIIIIIIIIIIXXIXIIIIIIIIIIXXIXII",
    "IIIIIIIIIIIIIIIXXIXIIIXXIXIIIXXIXIIIXXIXIIIIIIIII",
    "IZZIZIIIZZIZIIIZZIZIIIZZIZIIIIIIIIIIIIIIIIIIIIIII",
    "IZZIZIIIIIIIIIIZZIZIIIIIIIIIIZZIZIIIIIIIIIIZZIZII",
    "IIIIIIIIIIIIIIIZZIZIIIZZIZIIIZZIZIIIZZIZIIIIIIIII"
]

num_qubits = 49

def solve_tableau():
    # Attempt to use Stim's Tableau.from_stabilizers if possible, but 
    # we don't have a full set of stabilizers (maybe).
    # Let's count them.
    print(f"Number of stabilizers: {len(stabilizers)}")

    # Check commutation
    commutes = True
    for i in range(len(stabilizers)):
        for j in range(i + 1, len(stabilizers)):
            s1 = stabilizers[i]
            s2 = stabilizers[j]
            
            # calculate anticommutation
            anticommutes = False
            # We can use a simpler check: count number of positions where they have different Paulis (ignoring I)
            # Actually, two Paulis anticommute if they differ and neither is I.
            # X and Z anticommute. X and Y anticommute. Y and Z anticommute.
            # I and anything commute. Same Paulis commute.
            
            # Vectorized check is better but let's just do loop for now.
            count = 0
            for k in range(num_qubits):
                p1 = s1[k]
                p2 = s2[k]
                if p1 == 'I' or p2 == 'I':
                    continue
                if p1 != p2:
                    count += 1
            
            if count % 2 == 1:
                print(f"Stabilizers {i} and {j} anticommute!")
                commutes = False

    if commutes:
        print("All stabilizers commute.")
    else:
        print("Some stabilizers anticommute.")
        return

    # Check independence using Gaussian elimination on symplectic matrix
    
    # Create symplectic matrix
    # Rows = stabilizers
    # Cols = 2 * num_qubits (X parts then Z parts)
    
    matrix = []
    for s in stabilizers:
        row = [0] * (2 * num_qubits)
        for k, p in enumerate(s):
            if p == 'X':
                row[k] = 1
            elif p == 'Z':
                row[k + num_qubits] = 1
            elif p == 'Y':
                row[k] = 1
                row[k + num_qubits] = 1
        matrix.append(row)
    
    mat_np = np.array(matrix, dtype=int)
    
    # Gaussian elimination over GF(2)
    def rank_gf2(mat):
        mat = mat.copy()
        rows, cols = mat.shape
        rank = 0
        pivot_row = 0
        for col in range(cols):
            if pivot_row >= rows:
                break
            # Find a row with 1 in this column
            swap_row = -1
            for r in range(pivot_row, rows):
                if mat[r, col] == 1:
                    swap_row = r
                    break
            
            if swap_row != -1:
                # Swap rows
                mat[[pivot_row, swap_row]] = mat[[swap_row, pivot_row]]
                
                # Eliminate other rows
                for r in range(rows):
                    if r != pivot_row and mat[r, col] == 1:
                        mat[r] ^= mat[pivot_row]
                
                pivot_row += 1
                rank += 1
        return rank

    r = rank_gf2(mat_np)
    print(f"Rank: {r}")
    
    if r == len(stabilizers):
        print("Stabilizers are independent.")
    else:
        print(f"Stabilizers are NOT independent. Rank {r} < {len(stabilizers)}")

    # Try to complete the set
    # Try using stim.Tableau.from_stabilizers directly with allow_underconstrained=True
    try:
        stim_stabilizers = [stim.PauliString(s) for s in stabilizers]
        # Check if we can find a state
        tableau = stim.Tableau.from_stabilizers(stim_stabilizers, allow_underconstrained=True, allow_redundant=True)
        
        # Convert to circuit
        # The tableau represents the operation U such that U|0> = |psi>.
        # Wait, no. Tableau represents the stabilizers of the state |psi> = U|0>.
        # Actually, a Tableau object T stores the mapping of Pauli generators.
        # T(Z_k) is the k-th stabilizer. T(X_k) is the k-th destabilizer.
        # If we use from_stabilizers, it constructs a Tableau whose Z outputs are the given stabilizers.
        # So we just need to invert the tableau operation to get the circuit that prepares the state?
        # NO. The Tableau *is* the operation (in Heisenberg picture).
        # If T maps Z_k to S_k, then the circuit for T prepares the state stabilized by S_k from |0>.
        # So we just need `tableau.to_circuit()`.
        
        circuit = tableau.to_circuit("elimination")
        print("Circuit generated successfully.")
        
        # Write to file
        with open("circuit_49_v3.stim", "w") as f:
            f.write(str(circuit))
            
    except Exception as e:
        print(f"Error generating circuit with stim: {e}")
        import traceback
        traceback.print_exc()

solve_tableau()


solve_tableau()
