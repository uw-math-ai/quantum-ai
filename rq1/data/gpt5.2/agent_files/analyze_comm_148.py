import numpy as np

def to_symplectic(s):
    n = len(s)
    xs = np.zeros(n, dtype=int)
    zs = np.zeros(n, dtype=int)
    for i, c in enumerate(s):
        if c == 'X':
            xs[i] = 1
        elif c == 'Z':
            zs[i] = 1
        elif c == 'Y':
            xs[i] = 1
            zs[i] = 1
    return xs, zs

def analyze():
    with open('stabilizers_148.txt', 'r') as f:
        lines = [line.strip() for line in f if line.strip()]
    
    tableau = []
    for i, line in enumerate(lines):
        x, z = to_symplectic(line)
        if len(x) != 148:
            print(f"Warning: line {i} has length {len(x)}")
        tableau.append((x, z))
    
    n_stabs = len(tableau)
    print(f"Number of stabilizers: {n_stabs}")
    
    anticommuting_pairs = []
    for i in range(n_stabs):
        x1, z1 = tableau[i]
        for j in range(i + 1, n_stabs):
            x2, z2 = tableau[j]
            comm = np.sum(x1 * z2 + x2 * z1) % 2
            if comm != 0:
                anticommuting_pairs.append((i, j))
    
    print(f"Found {len(anticommuting_pairs)} anticommuting pairs.")
    for i, j in anticommuting_pairs:
        print(f"  {i} vs {j}")
        # Print the relevant parts
        s1 = lines[i]
        s2 = lines[j]
        # Find collision indices
        collisions = []
        for k in range(len(s1)):
            c1 = s1[k]
            c2 = s2[k]
            if c1 != 'I' and c2 != 'I':
                # check if they commute at this site
                # X and Z anticommute, Y and Z anticommute, X and Y anticommute
                # I.e. different non-identity Paulis
                if c1 != c2:
                    collisions.append(k)
        print(f"    Collisions at: {collisions}")

analyze()
