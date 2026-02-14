import stim
import numpy as np

def solve():
    stabilizers_str = [
        "XXXXIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIII",
        "IIIIIIIXXXXIIIIIIIIIIIIIIIIIIIIIIIIIIIIIII",
        "IIIIIIIIIIIIIIXXXXIIIIIIIIIIIIIIIIIIIIIIII",
        "IIIIIIIIIIIIIIIIIIIIIXXXXIIIIIIIIIIIIIIIII",
        "IIIIIIIIIIIIIIIIIIIIIIIIIIIIXXXXIIIIIIIIII",
        "IIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIXXXXIII",
        "XIXIXIXIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIII",
        "IIIIIIIXIXIXIXIIIIIIIIIIIIIIIIIIIIIIIIIIII",
        "IIIIIIIIIIIIIIXIXIXIXIIIIIIIIIIIIIIIIIIIII",
        "IIIIIIIIIIIIIIIIIIIIIXIXIXIXIIIIIIIIIIIIII",
        "IIIIIIIIIIIIIIIIIIIIIIIIIIIIXIXIXIXIIIIIII",
        "IIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIXIXIXIX",
        "IIXXXXIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIII",
        "IIIIIIIIIXXXXIIIIIIIIIIIIIIIIIIIIIIIIIIIII",
        "IIIIIIIIIIIIIIIIXXXXIIIIIIIIIIIIIIIIIIIIII",
        "IIIIIIIIIIIIIIIIIIIIIIIXXXXIIIIIIIIIIIIIII",
        "IIIIIIIIIIIIIIIIIIIIIIIIIIIIIIXXXXIIIIIIII",
        "IIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIXXXXI",
        "ZZZZIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIII",
        "IIIIIIIZZZZIIIIIIIIIIIIIIIIIIIIIIIIIIIIIII",
        "IIIIIIIIIIIIIIZZZZIIIIIIIIIIIIIIIIIIIIIIII",
        "IIIIIIIIIIIIIIIIIIIIIZZZZIIIIIIIIIIIIIIIII",
        "IIIIIIIIIIIIIIIIIIIIIIIIIIIIZZZZIIIIIIIIII",
        "IIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIZZZZIII",
        "ZIZIZIZIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIII",
        "IIIIIIIZIZIZIZIIIIIIIIIIIIIIIIIIIIIIIIIIII",
        "IIIIIIIIIIIIIIZIZIZIZIIIIIIIIIIIIIIIIIIIII",
        "IIIIIIIIIIIIIIIIIIIIIZIZIZIZIIIIIIIIIIIIII",
        "IIIIIIIIIIIIIIIIIIIIIIIIIIIIZIZIZIZIIIIIII",
        "IIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIZIZIZIZ",
        "IIZZZZIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIII",
        "IIIIIIIIIZZZZIIIIIIIIIIIIIIIIIIIIIIIIIIIII",
        "IIIIIIIIIIIIIIIIZZZZIIIIIIIIIIIIIIIIIIIIII",
        "IIIIIIIIIIIIIIIIIIIIIIIZZZZIIIIIIIIIIIIIIIII",
        "IIIIIIIIIIIIIIIIIIIIIIIIIIIIIIZZZZIIIIIIII",
        "IIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIZZZZI",
        "IXXIXIIIXXIXIIIXXIXIIIXXIXIIIXXIXIIIXXIXII",
        "IZZIZIIIZZIZIIIZZIZIIIZZIZIIIZZIZIIIZZIZII"
    ]
    
    # Fix typo in stabilizer 33 (index 33, 34th in list)
    # The list above has 38 lines.
    # Line 34: "IIIIIIIIIIIIIIIIIIIIIIIZZZZIIIIIIIIIIIIIIIII" -> Length 44? 
    # Wait, let me check the input carefully.
    # "IIIIIIIIIIIIIIIIIIIIIIIZZZZIIIIIIIIIIIIIII" -> length 42.
    # In my copy-paste above I might have added extra chars.
    # Let's clean it up.
    
    stabilizers_str = [
        "XXXXIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIII",
        "IIIIIIIXXXXIIIIIIIIIIIIIIIIIIIIIIIIIIIIIII",
        "IIIIIIIIIIIIIIXXXXIIIIIIIIIIIIIIIIIIIIIIII",
        "IIIIIIIIIIIIIIIIIIIIIXXXXIIIIIIIIIIIIIIIII",
        "IIIIIIIIIIIIIIIIIIIIIIIIIIIIXXXXIIIIIIIIII",
        "IIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIXXXXIII",
        "XIXIXIXIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIII",
        "IIIIIIIXIXIXIXIIIIIIIIIIIIIIIIIIIIIIIIIIII",
        "IIIIIIIIIIIIIIXIXIXIXIIIIIIIIIIIIIIIIIIIII",
        "IIIIIIIIIIIIIIIIIIIIIXIXIXIXIIIIIIIIIIIIII",
        "IIIIIIIIIIIIIIIIIIIIIIIIIIIIXIXIXIXIIIIIII",
        "IIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIXIXIXIX",
        "IIXXXXIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIII",
        "IIIIIIIIIXXXXIIIIIIIIIIIIIIIIIIIIIIIIIIIII",
        "IIIIIIIIIIIIIIIIXXXXIIIIIIIIIIIIIIIIIIIIII",
        "IIIIIIIIIIIIIIIIIIIIIIIXXXXIIIIIIIIIIIIIII",
        "IIIIIIIIIIIIIIIIIIIIIIIIIIIIIIXXXXIIIIIIII",
        "IIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIXXXXI",
        "ZZZZIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIII",
        "IIIIIIIZZZZIIIIIIIIIIIIIIIIIIIIIIIIIIIIIII",
        "IIIIIIIIIIIIIIZZZZIIIIIIIIIIIIIIIIIIIIIIII",
        "IIIIIIIIIIIIIIIIIIIIIZZZZIIIIIIIIIIIIIIIII",
        "IIIIIIIIIIIIIIIIIIIIIIIIIIIIZZZZIIIIIIIIII",
        "IIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIZZZZIII",
        "ZIZIZIZIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIII",
        "IIIIIIIZIZIZIZIIIIIIIIIIIIIIIIIIIIIIIIIIII",
        "IIIIIIIIIIIIIIZIZIZIZIIIIIIIIIIIIIIIIIIIII",
        "IIIIIIIIIIIIIIIIIIIIIZIZIZIZIIIIIIIIIIIIII",
        "IIIIIIIIIIIIIIIIIIIIIIIIIIIIZIZIZIZIIIIIII",
        "IIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIZIZIZIZ",
        "IIZZZZIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIII",
        "IIIIIIIIIZZZZIIIIIIIIIIIIIIIIIIIIIIIIIIIII",
        "IIIIIIIIIIIIIIIIZZZZIIIIIIIIIIIIIIIIIIIIII",
        "IIIIIIIIIIIIIIIIIIIIIIIZZZZIIIIIIIIIIIIIII",
        "IIIIIIIIIIIIIIIIIIIIIIIIIIIIIIZZZZIIIIIIII",
        "IIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIZZZZI",
        "IXXIXIIIXXIXIIIXXIXIIIXXIXIIIXXIXIIIXXIXII",
        "IZZIZIIIZZIZIIIZZIZIIIZZIZIIIZZIZIIIZZIZII"
    ]
    
    num_qubits = 42
    
    # Verify lengths
    for i, s in enumerate(stabilizers_str):
        if len(s) != num_qubits:
            print(f"Error: Stabilizer {i} has length {len(s)}")
            return

    stabs = [stim.PauliString(s) for s in stabilizers_str]
    
    # 1. Complete the stabilizer set to 42
    # We need 4 more.
    # We can use the tableau method from previous script logic but implemented cleanly here.
    
    # Helper to check independence and commutativity
    def solve_completion():
        # Current stabilizers as binary matrix
        # Columns: X0..Xn-1, Z0..Zn-1
        
        def to_binary_row(p):
            row = np.zeros(2*num_qubits, dtype=np.uint8)
            for k in range(num_qubits):
                # p[k] returns 0=I, 1=X, 2=Y, 3=Z
                # We need X, Z components.
                # X=1 -> X=1, Z=0
                # Y=2 -> X=1, Z=1
                # Z=3 -> X=0, Z=1
                # I=0 -> X=0, Z=0
                val = p[k]
                if val == 1 or val == 2: row[k] = 1
                if val == 3 or val == 2: row[k + num_qubits] = 1
            return row
            
        def from_binary_row(row):
            s = ""
            for k in range(num_qubits):
                x = row[k]
                z = row[k + num_qubits]
                if x and z: s += "Y"
                elif x: s += "X"
                elif z: s += "Z"
                else: s += "I"
            return stim.PauliString(s)
            
        current_rows = [to_binary_row(s) for s in stabs]
        
        # We need to find vectors that are orthogonal to all current rows under symplectic product.
        # Symplectic product of u, v is u @ J @ v.
        # J = [[0, I], [I, 0]].
        
        # Build check matrix H (38 x 84)
        H = np.array(current_rows, dtype=np.uint8)
        
        # We want x such that H @ J @ x = 0.
        # Let A = H @ J.
        # We find null space of A.
        
        J = np.zeros((2*num_qubits, 2*num_qubits), dtype=np.uint8)
        for k in range(num_qubits):
            J[k, k + num_qubits] = 1
            J[k + num_qubits, k] = 1
            
        A = (H @ J) % 2
        
        # Gaussian elimination on A to find null space basis
        # A is 38 x 84.
        rows, cols = A.shape
        mat = A.copy()
        pivots = []
        
        pivot_row = 0
        pivot_col_to_row = {}
        
        for c in range(cols):
            if pivot_row >= rows: break
            
            # Find pivot
            swap = -1
            for r in range(pivot_row, rows):
                if mat[r, c] == 1:
                    swap = r
                    break
            
            if swap != -1:
                mat[[pivot_row, swap]] = mat[[swap, pivot_row]]
                # Eliminate
                for r in range(rows):
                    if r != pivot_row and mat[r, c] == 1:
                        mat[r] ^= mat[pivot_row]
                
                pivot_col_to_row[c] = pivot_row
                pivots.append(c)
                pivot_row += 1
                
        # Find free columns
        free_cols = [c for c in range(cols) if c not in pivots]
        
        null_basis = []
        for free in free_cols:
            vec = np.zeros(cols, dtype=np.uint8)
            vec[free] = 1
            # Back sub
            for p in reversed(pivots):
                r = pivot_col_to_row[p]
                # mat[r, p] is 1.
                # mat[r, free] might be 1.
                # sum(mat[r, k] * vec[k]) = 0
                val = 0
                for k in range(p + 1, cols):
                    if mat[r, k] == 1:
                        val ^= vec[k]
                vec[p] = val
            null_basis.append(vec)
            
        # Convert null basis to Pauli strings
        candidates = [from_binary_row(v) for v in null_basis]
        
        # Now we pick 4 that extend the group.
        # We need to maintain commutativity (all candidates commute with initial S, but must commute with each other).
        # And independence.
        
        final_stabs = list(stabs)
        
        for cand in candidates:
            if len(final_stabs) == 42: break
            
            # Check commutativity with newly added
            commutes = True
            for s in final_stabs[38:]:
                if not cand.commutes(s):
                    commutes = False
                    break
            if not commutes: continue
            
            # Check independence
            # Quick hack: check if adding it increases rank of binary matrix
            
            # Form matrix of current + candidate
            curr_bin = np.array([to_binary_row(s) for s in final_stabs] + [to_binary_row(cand)], dtype=np.uint8)
            
            # Rank check
            def get_rank(m):
                m = m.copy()
                pr = 0
                rs, cs = m.shape
                for c in range(cs):
                    if pr >= rs: break
                    sw = -1
                    for r in range(pr, rs):
                        if m[r, c] == 1:
                            sw = r
                            break
                    if sw != -1:
                        m[[pr, sw]] = m[[sw, pr]]
                        for r in range(rs):
                            if r != pr and m[r, c] == 1:
                                m[r] ^= m[pr]
                        pr += 1
                return pr
                
            if get_rank(curr_bin) == len(final_stabs) + 1:
                final_stabs.append(cand)
                print(f"Added stabilizer {len(final_stabs)}")
                
        return final_stabs

    final_stabs = solve_completion()
    
    if len(final_stabs) != 42:
        print(f"Failed to find 42 stabilizers. Found {len(final_stabs)}")
        return

    # Use Stim to generate circuit
    # stim.Tableau.from_stabilizers creates a Tableau.
    # Then to_circuit() creates a circuit that prepares the state.
    
    try:
        t = stim.Tableau.from_stabilizers(final_stabs)
        circ = t.to_circuit("elimination")
        
        with open("circuit_attempt.stim", "w") as f:
            f.write(str(circ))
        print("Circuit generated in circuit_attempt.stim")
        
    except Exception as e:
        print(f"Error generating circuit: {e}")

if __name__ == "__main__":
    solve()
