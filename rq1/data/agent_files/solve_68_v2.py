import stim
import numpy as np

def symplectic_inner_product(p1, p2):
    # p1, p2 are numpy arrays of shape (2n,)
    n = len(p1) // 2
    x1 = p1[:n]
    z1 = p1[n:]
    x2 = p2[:n]
    z2 = p2[n:]
    return (np.dot(x1, z2) + np.dot(z1, x2)) % 2

def str_to_pauli(s):
    n = len(s)
    x = np.zeros(n, dtype=np.uint8)
    z = np.zeros(n, dtype=np.uint8)
    for i, c in enumerate(s):
        if c in 'XY': x[i] = 1
        if c in 'ZY': z[i] = 1
    return np.concatenate([x, z])

def pauli_to_str(p):
    n = len(p) // 2
    x = p[:n]
    z = p[n:]
    chars = []
    for i in range(n):
        if x[i] and z[i]: chars.append('Y')
        elif x[i]: chars.append('X')
        elif z[i]: chars.append('Z')
        else: chars.append('I')
    return "".join(chars)

def solve():
    with open("stabilizers_68.txt", 'r') as f:
        lines = [l.strip() for l in f if l.strip()]
    
    n_qubits = len(lines[0])
    stabilizers = [str_to_pauli(l) for l in lines]
    stab_matrix = np.array(stabilizers, dtype=np.uint8)
    
    current_stabs = list(stab_matrix)
    
    candidates = []
    # Try all single qubit X and Z
    for i in range(n_qubits):
        z_cand = np.zeros(2*n_qubits, dtype=np.uint8)
        z_cand[n_qubits + i] = 1
        candidates.append(z_cand)
        x_cand = np.zeros(2*n_qubits, dtype=np.uint8)
        x_cand[i] = 1
        candidates.append(x_cand)
        
    def get_rank(mat):
        m, n = mat.shape
        mat = mat.copy()
        pivot_row = 0
        for col in range(n):
            if pivot_row >= m: break
            if mat[pivot_row, col] == 0:
                swap = -1
                for r in range(pivot_row + 1, m):
                    if mat[r, col] == 1:
                        swap = r
                        break
                if swap != -1:
                    mat[[pivot_row, swap]] = mat[[swap, pivot_row]]
                else:
                    continue
            
            for r in range(pivot_row + 1, m):
                if mat[r, col]:
                    mat[r] = (mat[r] + mat[pivot_row]) % 2
            pivot_row += 1
        return pivot_row

    added_stabs = []
    
    # Try to add until rank is 68
    initial_rank = get_rank(stab_matrix)
    print(f"Initial rank: {initial_rank}")
    
    current_rank = initial_rank
    
    for cand in candidates:
        if len(added_stabs) == (n_qubits - initial_rank): break
        
        # Check commutativity with ALL current stabs (original + added)
        commutes = True
        for s in current_stabs + added_stabs:
            if symplectic_inner_product(cand, s) != 0:
                commutes = False
                break
        if not commutes: continue
        
        # Check independence
        new_mat = np.array(current_stabs + added_stabs + [cand])
        new_rank = get_rank(new_mat)
        if new_rank > current_rank:
            added_stabs.append(cand)
            current_rank = new_rank
            print(f"Added stabilizer: {pauli_to_str(cand)}")

    full_stabilizers = current_stabs + added_stabs
    print(f"Total stabilizers: {len(full_stabilizers)}")
    
    # Convert to stim PauliStrings
    sim_stabs = []
    for s in full_stabilizers:
        sim_stabs.append(stim.PauliString(pauli_to_str(s)))
        
    print("Synthesizing circuit with stim...")
    try:
        # stim.Tableau.from_stabilizers creates a Tableau whose stabilizers are the given list.
        # It automatically fills in the destabilizers if the list is full rank.
        t = stim.Tableau.from_stabilizers(sim_stabs)
        circuit = t.to_circuit()
        
        # Write to file
        with open("circuit_68.stim", "w") as f:
            f.write(str(circuit))
        print("Circuit written to circuit_68.stim")
            
    except Exception as e:
        print(f"Error during synthesis: {e}")

if __name__ == "__main__":
    solve()
