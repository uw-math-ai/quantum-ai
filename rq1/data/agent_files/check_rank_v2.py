import stim
import numpy as np

def check_rank():
    stabilizers_str = [
        "XZZXIIIIIIIIIIIIIIIIIIIII",
        "IIIIIXZZXIIIIIIIIIIIIIIII",
        "IIIIIIIIIIXZZXIIIIIIIIIII",
        "IIIIIIIIIIIIIIIXZZXIIIIII",
        "IIIIIIIIIIIIIIIIIIIIXZZXI",
        "IXZZXIIIIIIIIIIIIIIIIIIII",
        "IIIIIIXZZXIIIIIIIIIIIIIII",
        "IIIIIIIIIIIXZZXIIIIIIIIII",
        "IIIIIIIIIIIIIIIIXZZXIIIII",
        "IIIIIIIIIIIIIIIIIIIIIXZZX",
        "XIXZZIIIIIIIIIIIIIIIIIIII",
        "IIIIIXIXZZIIIIIIIIIIIIIII",
        "IIIIIIIIIIXIXZZIIIIIIIIII",
        "IIIIIIIIIIIIIIIXIXZZIIIII",
        "IIIIIIIIIIIIIIIIIIIIXIXZZ",
        "ZXIXZIIIIIIIIIIIIIIIIIIII",
        "IIIIIZXIXZIIIIIIIIIIIIIII",
        "IIIIIIIIIIZXIXZIIIIIIIIII",
        "IIIIIIIIIIIIIIIZXIXZIIIII",
        "IIIIIIIIIIIIIIIIIIIIZXIXZ",
        "XXXXXZZZZZZZZZZXXXXXIIIII",
        "IIIIIXXXXXZZZZZZZZZZXXXXX",
        "XXXXXIIIIIXXXXXZZZZZZZZZZ",
        "ZZZZZXXXXXIIIIIXXXXXZZZZZ"
    ]
    
    n = 25
    m = len(stabilizers_str)
    
    xs = np.zeros((m, n), dtype=int)
    zs = np.zeros((m, n), dtype=int)
    
    for i, s in enumerate(stabilizers_str):
        for j, char in enumerate(s):
            if char == 'X': xs[i, j] = 1
            elif char == 'Z': zs[i, j] = 1
            elif char == 'Y': xs[i, j] = 1; zs[i, j] = 1
            
    mat = np.concatenate([xs, zs], axis=1)
    
    def get_rank(rows):
        rows = np.array(rows, dtype=int, copy=True)
        pivot_row = 0
        pivot_col = 0
        height, width = rows.shape
        while pivot_row < height and pivot_col < width:
            if rows[pivot_row, pivot_col] == 0:
                swap = -1
                for r in range(pivot_row, height):
                    if rows[r, pivot_col] == 1:
                        swap = r
                        break
                if swap == -1:
                    pivot_col += 1
                    continue
                rows[[pivot_row, swap]] = rows[[swap, pivot_row]]
            
            for i in range(pivot_row + 1, height):
                if rows[i, pivot_col] == 1:
                    rows[i] ^= rows[pivot_row]
            pivot_row += 1
            pivot_col += 1
        return pivot_row

    rank = get_rank(mat)
    print(f"Rank: {rank}")
    
    if rank == 24:
        # Find something that commutes with all stabilizers
        # Random search is easy
        found_comm = None
        for _ in range(10000):
             c = np.random.randint(0, 2, 2*n)
             # Check commutation
             commutes = True
             # Symplectic product with all rows
             for i in range(m):
                 res = 0
                 for k in range(n):
                     res ^= (mat[i, k] * c[k+n]) ^ (mat[i, k+n] * c[k])
                 if res == 1:
                     commutes = False
                     break
             if commutes:
                 # Check independence
                 if get_rank(np.vstack([mat, c])) > rank:
                     found_comm = c
                     break
        
        if found_comm is not None:
            s_list = []
            for k in range(n):
                if found_comm[k] and found_comm[k+n]: s_list.append('Y')
                elif found_comm[k]: s_list.append('X')
                elif found_comm[k+n]: s_list.append('Z')
                else: s_list.append('I')
            s_str = "".join(s_list)
            print(f"Logical: {s_str}")
            
            full_stabilizers = stabilizers_str + [s_str]
            t = stim.Tableau.from_stabilizers([stim.PauliString(s) for s in full_stabilizers])
            circuit = t.to_circuit()
            with open("circuit_solution.stim", "w") as f:
                f.write(str(circuit))
            print("Circuit generated.")

if __name__ == "__main__":
    check_rank()
