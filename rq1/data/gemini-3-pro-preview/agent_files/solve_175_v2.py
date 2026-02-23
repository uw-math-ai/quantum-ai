
import stim
import sys
import os

# Add the directory to sys.path
sys.path.append(os.path.join(os.getcwd(), 'data', 'gemini-3-pro-preview', 'agent_files'))

# Read fixed generators
with open(os.path.join(os.getcwd(), 'data', 'gemini-3-pro-preview', 'agent_files', 'stabilizers_175_fixed.txt'), 'r') as f:
    generators_str = [line.strip() for line in f]

generators = [stim.PauliString(g) for g in generators_str]
print(f"Loaded {len(generators)} generators")

# Check commutativity
print("Checking commutativity...")
for i in range(len(generators)):
    for j in range(i + 1, len(generators)):
        if not generators[i].commutes(generators[j]):
            print(f"Generators {i} and {j} anticommute!")
            sys.exit(1)

print("All stabilizers commute.")

# Try to complete the basis
current_generators = list(generators)

# Candidates: X_i, Z_i
candidates = []
for q in range(175):
    for p in [1, 3]: # X, Z
        candidate = stim.PauliString(175)
        candidate[q] = p
        candidates.append(candidate)

# We need 175 generators
# We have 174.
# But maybe they are dependent.
# Let's try to add candidates until we hit 175 independent ones.
# But we can't easily check independence incrementally with Stim.
# Strategy:
# Keep adding candidates that commute with everything in current_generators.
# Once we have >= 175, try to pick a subset of size 175 that works?
# Or just try to find 1 that makes the set valid.

# If the rank is 174, we need 1 more.
# If rank is 173, we need 2 more.

# Let's try to build a tableau from scratch using Gaussian elimination in python?
# It's a bit of work to implement.

# Alternative:
# Use `stim.Tableau.from_conjugated_generators`? No.

# Let's try to assume rank is 174 first.
# If we find a candidate that works, great.
# We tried that and it failed.
# This suggests rank < 174 OR no single-qubit operator works (unlikely for stabilizer codes, usually there's a logical operator that is simple).
# Or maybe the "fixed" generators are dependent.
# If rank is 173, then adding 1 candidate gives rank 174. Still fails `from_stabilizers`.

# Let's implement a simple Gaussian elimination to find rank and independent set.
def to_tableau(pauli_strings):
    n = len(pauli_strings[0])
    m = len(pauli_strings)
    # 2n columns (x, z). m rows.
    # We use boolean GF(2).
    mat = []
    for p in pauli_strings:
        row = []
        for k in range(n):
            # X check
            row.append(p[k] in [1, 2]) # X or Y
            # Z check
            row.append(p[k] in [2, 3]) # Y or Z
        mat.append(row)
    return mat

def gaussian_elimination(mat):
    rows = len(mat)
    cols = len(mat[0])
    pivot_row = 0
    independent_indices = []
    
    for col in range(cols):
        if pivot_row >= rows:
            break
            
        # Find pivot
        pivot = -1
        for r in range(pivot_row, rows):
            if mat[r][col]:
                pivot = r
                break
        
        if pivot == -1:
            continue
            
        # Swap
        mat[pivot_row], mat[pivot] = mat[pivot], mat[pivot_row]
        if pivot_row == pivot:
             # If we didn't swap, this index was already here.
             pass
        else:
             # We swapped a row into pivot position.
             # We need to track original indices if we want the independent subset.
             pass

        # Eliminate
        for r in range(rows):
            if r != pivot_row and mat[r][col]:
                for c in range(col, cols):
                    mat[r][c] ^= mat[pivot_row][c]
        
        pivot_row += 1
        
    return pivot_row # Rank

mat = to_tableau(current_generators)
rank = gaussian_elimination(mat)
print(f"Rank of generators: {rank}")

if rank < 175:
    needed = 175 - rank
    print(f"Need {needed} more independent generators.")
    
    # Try to add candidates
    added_count = 0
    for cand in candidates:
        if added_count == needed:
            break
            
        # Check commutativity with ALL current generators
        commutes_all = True
        for g in current_generators:
            if not cand.commutes(g):
                commutes_all = False
                break
        
        if not commutes_all:
            continue

        # Check independence
        # Add to temp list and check rank
        temp_gens = current_generators + [cand]
        mat = to_tableau(temp_gens)
        new_rank = gaussian_elimination(mat)
        
        if new_rank > rank:
            print(f"Added generator {cand}")
            current_generators.append(cand)
            rank = new_rank
            added_count += 1
            break # Found one!

if rank == 175:
    # Now we have 175 independent commuting generators?
    # Wait, we checked commutativity with ORIGINAL generators.
    # We also need to check if new generators commute with EACH OTHER.
    # My loop checked `cand.commutes(g) for g in current_generators`.
    # `current_generators` grows, so it checks against previously added candidates too.
    # Correct.
    
    # But wait, `current_generators` might have more than 175 elements if we started with dependent ones?
    # No, rank calculation doesn't remove dependent ones from the list, it just tells us the rank.
    # If the original set was dependent, we still have 174 elements but rank < 174.
    # We added elements to increase rank.
    # Now we have 174 + needed elements.
    # We need to extract a basis of size 175.
    
    # Let's just pass the whole list to Stim?
    # Stim `from_stabilizers` might complain if > 175 generators.
    # We need exactly 175 independent ones.
    
    # Let's pick the independent ones using Gaussian elimination again but tracking indices.
    
    def get_basis(pauli_strings):
        n = len(pauli_strings[0])
        # mat with indices
        mat = []
        for i, p in enumerate(pauli_strings):
            row = []
            for k in range(n):
                row.append(p[k] in [1, 2])
                row.append(p[k] in [2, 3])
            mat.append((row, i))
            
        rows = len(mat)
        cols = 2 * n
        pivot_row = 0
        basis_indices = []
        
        for col in range(cols):
            if pivot_row >= rows:
                break
            
            pivot = -1
            for r in range(pivot_row, rows):
                if mat[r][0][col]:
                    pivot = r
                    break
            
            if pivot == -1:
                continue
                
            mat[pivot_row], mat[pivot] = mat[pivot], mat[pivot_row]
            basis_indices.append(mat[pivot_row][1])
            
            for r in range(rows):
                if r != pivot_row and mat[r][0][col]:
                    for c in range(col, cols):
                        mat[r][0][c] ^= mat[pivot_row][0][c]
            
            pivot_row += 1
            
        return [pauli_strings[i] for i in basis_indices]

    basis = get_basis(current_generators)
    print(f"Basis size: {len(basis)}")
    
    if len(basis) == 175:
        try:
            tableau = stim.Tableau.from_stabilizers(basis)
            circuit = tableau.to_circuit("mp")
            print("Circuit generated successfully")
            with open(os.path.join(os.getcwd(), 'data', 'gemini-3-pro-preview', 'agent_files', 'circuit_175.stim'), 'w') as f:
                f.write(str(circuit))
        except Exception as e:
            print(f"Error: {e}")
    else:
        print(f"Basis size is {len(basis)}, expected 175.")

else:
    print(f"Still need {175 - rank} generators.")
