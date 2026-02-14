import stim
import numpy as np
import galois

stabilizers = [
    "IIXIXXXIIIIIIIIIIIIIIIIIIIII",
    "IIIIIIIIIXIXXXIIIIIIIIIIIIII",
    "IIIIIIIIIIIIIIIIXIXXXIIIIIII",
    "IIIIIIIIIIIIIIIIIIIIIIIXIXXX",
    "IXIXIXXIIIIIIIIIIIIIIIIIIIII",
    "IIIIIIIIXIXIXXIIIIIIIIIIIIII",
    "IIIIIIIIIIIIIIIXIXIXXIIIIIII",
    "IIIIIIIIIIIIIIIIIIIIIIXIXIXX",
    "XXXIIXIIIIIIIIIIIIIIIIIIIIII",
    "IIIIIIIXXXIIXIIIIIIIIIIIIIII",
    "IIIIIIIIIIIIIIXXXIIXIIIIIIII",
    "IIIIIIIIIIIIIIIIIIIIIXXXIIXI",
    "IIZIZZZIIIIIIIIIIIIIIIIIIIII",
    "IIIIIIIIIZIZZZIIIIIIIIIIIIII",
    "IIIIIIIIIIIIIIIIZIZZZIIIIIII",
    "IIIIIIIIIIIIIIIIIIIIIIIZIZZZ",
    "IZIZIZZIIIIIIIIIIIIIIIIIIIII",
    "IIIIIIIIZIZIZZIIIIIIIIIIIIII",
    "IIIIIIIIIIIIIIIZIZIZZIIIIIII",
    "IIIIIIIIIIIIIIIIIIIIIIZIZIZZ",
    "ZZZIIZIIIIIIIIIIIIIIIIIIIIII",
    "IIIIIIIZZZIIZIIIIIIIIIIIIIII",
    "IIIIIIIIIIIIIIZZZIIZIIIIIIII",
    "IIIIIIIIIIIIIIIIIIIIIZZZIIZI",
    "XXIXIIIXXIXIIIXXIXIIIXXIXIII",
    "ZZIZIIIZZIZIIIZZIZIIIZZIZIII"
]

n = 28
num_stabs = len(stabilizers)

def str_to_xz(s):
    x = np.array([1 if c in 'XY' else 0 for c in s], dtype=int)
    z = np.array([1 if c in 'ZY' else 0 for c in s], dtype=int)
    return x, z

# Construct check matrix H = (X|Z)
H_x = []
H_z = []
for s in stabilizers:
    x, z = str_to_xz(s)
    H_x.append(x)
    H_z.append(z)

H = np.hstack([np.array(H_x), np.array(H_z)])
# H is 26 x 56

# To find logical operators, we find the kernel of the symplectic form.
# The symplectic form is J = [[0, I], [I, 0]].
# We want vectors v such that v * J * H^T = 0.
# i.e. v commutes with all rows of H.
# Let G be the generator matrix of the kernel.
# The rows of H are in the kernel (since stabilizers commute).
# Since rank(H) = 26 (assumed), the kernel has dimension 56 - 26 = 30.
# The stabilizers account for 26 dimensions.
# So there are 4 logical operators (X_L1, Z_L1, X_L2, Z_L2).
# We need to find them.

# Let's solve H * J * v^T = 0 over GF(2).
# H_tilde = H * J.
# H * J = (H_x, H_z) * [[0, I], [I, 0]] = (H_z, H_x)
# So we solve (H_z, H_x) * v^T = 0.

H_tilde = np.hstack([np.array(H_z), np.array(H_x)])
# Solve H_tilde * v = 0 using galois
GF2 = galois.GF(2)
H_gf = GF2(H_tilde)
null_space = H_gf.null_space()
# null_space is a matrix where rows are basis vectors of the kernel.
# Dimension should be 30.

print(f"Null space dimension: {null_space.shape[0]}")

# The null space contains the stabilizers themselves.
# We need to filter out the stabilizers.
# But actually, we just need to pick *any* 2 operators from the null space
# such that they commute with each other and are independent of the stabilizers (and each other).
# And together with stabilizers form a commuting set of size 28.
# Actually, if we pick ANY vector from null space, it commutes with all stabilizers.
# We just need to make sure it's independent of stabilizers.
# And if we pick two, they must commute with each other.

# Convert null_space to numpy
kernel_basis = np.array(null_space, dtype=int)

# Check independence from stabilizers
# We can just incrementally add vectors from kernel_basis to the stabilizer set
# until we reach 28.
# We check commutation with previously added ones.

current_x = list(np.array(H_x))
current_z = list(np.array(H_z))

added_count = 0
for i in range(kernel_basis.shape[0]):
    if added_count == 2:
        break
        
    vec = kernel_basis[i]
    # vec is (z_part, x_part) because we solved (H_z, H_x) * v = 0
    # Wait, v = (v_x, v_z)^T.
    # H_tilde * v = H_z * v_x + H_x * v_z = 0 (commutation condition).
    # So vec corresponds to v.
    # The first n components are v_x, second n are v_z.
    
    cand_x = vec[:n]
    cand_z = vec[n:]
    
    # Check if this candidate commutes with ALL current stabilizers (including newly added ones)
    # It definitely commutes with original 26.
    # We need to check with the ones we added.
    
    commutes_all = True
    for k in range(len(current_x)):
        if (np.sum(cand_x * current_z[k] + cand_z * current_x[k]) % 2) != 0:
            commutes_all = False
            break
            
    if not commutes_all:
        continue
        
    # Check independence
    temp_x = np.vstack([current_x, cand_x])
    temp_z = np.vstack([current_z, cand_z])
    
    gf_x = GF2(temp_x)
    gf_z = GF2(temp_z)
    tableau = np.concatenate((gf_x, gf_z), axis=1)
    rank = np.linalg.matrix_rank(tableau)
    
    if rank == len(current_x) + 1:
        current_x.append(cand_x)
        current_z.append(cand_z)
        added_count += 1
        print(f"Added stabilizer {added_count}")

if len(current_x) < 28:
    print("Failed to find enough commuting stabilizers")
else:
    print("Found full set of 28 stabilizers")
    
    # Now generate circuit
    stim_stabilizers = []
    for i in range(28):
        s = ""
        for k in range(n):
            x = current_x[i][k]
            z = current_z[i][k]
            if x and z: s += "Y"
            elif x: s += "X"
            elif z: s += "Z"
            else: s += "_"
        stim_stabilizers.append(stim.PauliString(s))
        
    try:
        tableau = stim.Tableau.from_stabilizers(stim_stabilizers)
        circuit = tableau.to_circuit()
        with open("circuit_28_full.stim", "w") as f:
            f.write(str(circuit))
        print("Circuit saved to circuit_28_full.stim")
        
    except Exception as e:
        print(f"Error: {e}")
