import stim
import numpy as np
import galois

# Stabilizers from the prompt
stabilizers = [
    "IIXIIXIIXXIIIIIIIII",
    "IIIIIIIIIIXIXIIIIXX",
    "IIIIIIIIIIXXIXIIIIX",
    "XXIIIIIIIIIIIIXXIII",
    "XXIXXIXIIIIIIIIIXII",
    "IIXIXIIIXIIIIIIIXII",
    "IXIIIIXXIIIIIIIXIII",
    "IIIXIIXXIIXXXIIIIII",
    "IIIXXIIIXXIXIXIIIII",
    "IIZIIZIIZZIIIIIIIII",
    "IIIIIIIIIIZIZIIIIZZ",
    "IIIIIIIIIIZZIZIIIIZ",
    "ZZIIIIIIIIIIIIZZIII",
    "ZZIZZIZIIIIIIIIIZII",
    "IIZIZIIIZIIIIIIIZII",
    "IZIIIIZZIIIIIIIZIII",
    "IIIZIIZZIIZZZIIIIII",
    "IIIZZIIIZZIZIZIIIII"
]

n_qubits = 19
GF = galois.GF(2)

def stab_to_vec(s):
    # Convert string to 2n vector [x1...xn z1...zn]
    xs = np.zeros(n_qubits, dtype=int)
    zs = np.zeros(n_qubits, dtype=int)
    for i, c in enumerate(s):
        if c in 'XY': xs[i] = 1
        if c in 'ZY': zs[i] = 1
    return np.concatenate((xs, zs))

stab_vecs = np.array([stab_to_vec(s) for s in stabilizers])

# Matrix for commutation check
# Commutation: v1 . Omega . v2 = 0
# Omega = [[0, I], [I, 0]]
def symplectic_inner_product(v1, v2):
    n = len(v1) // 2
    x1 = v1[:n]
    z1 = v1[n:]
    x2 = v2[:n]
    z2 = v2[n:]
    return (np.dot(x1, z2) + np.dot(z1, x2)) % 2

# Verify provided stabilizers commute
for i in range(len(stabilizers)):
    for j in range(i+1, len(stabilizers)):
        if symplectic_inner_product(stab_vecs[i], stab_vecs[j]) != 0:
            print(f"Error: Stabilizers {i} and {j} anti-commute!")
            exit(1)

# Find 19th stabilizer
# We look for a vector v such that v commutes with all stab_vecs
# AND v is linearly independent from stab_vecs.
# To find vectors that commute with all stabs, we solve H * Omega * v = 0
# where H is the matrix of stab_vecs.

Omega = np.zeros((2*n_qubits, 2*n_qubits), dtype=int)
for i in range(n_qubits):
    Omega[i, n_qubits+i] = 1
    Omega[n_qubits+i, i] = 1

H_comm = np.dot(stab_vecs, Omega) % 2
# Null space of H_comm over GF(2)
# galois library expects standard matrix
H_comm_gf = GF(H_comm)
null_space = H_comm_gf.null_space()

# null_space contains the stabilizers themselves (since they are isotropic) plus the logical operators.
# We need to find one vector in null_space that is not in the span of stab_vecs.
stab_space_gf = GF(stab_vecs)

found_19th = None

# Iterate through basis of null space
# Or just try random combinations?
# null_space is a basis for the centralizer.
# The centralizer has dimension 2n - k + k = 2n (if k=0) no.
# k=18 stabilizers. Subspace is 2^1.
# Centralizer dimension = n + (n-k) = 19 + 1 = 20.
# Wait.
# Number of physical qubits n=19.
# Number of stabilizers k=18.
# Commutant has dimension 2n - k = 38 - 18 = 20?
# No.
# The space of all Pauli operators is 2n = 38.
# The stabilizer group S has rank k=18.
# The centralizer C(S) contains S.
# Dimension of C(S) is 2n - k = 38 - 18 = 20.
# S is a subspace of C(S) of dimension 18.
# So C(S)/S has dimension 20 - 18 = 2.
# This corresponds to the logical X and Z operators (encoded qubit).
# We need any operator from C(S) that is not in S.
# It will act as a logical operator. Adding it to S gives a stabilizer group of rank 19 (pure state).

import random

# Convert null_space basis to numpy arrays
null_basis = np.array(null_space, dtype=int)
# Convert stab_space to numpy
stab_basis = np.array(stab_space_gf, dtype=int)

# Just check each basis element of null_space
for v in null_basis:
    # Check if v is in stab_space
    # Form matrix [stab_basis; v] and check rank
    mat = np.vstack([stab_basis, v])
    rank = np.linalg.matrix_rank(GF(mat))
    if rank == 19:
        found_19th = v
        break

if found_19th is None:
    # Try combinations?
    # Actually, with dimension difference 2, at least one basis vector must be outside.
    # Unless the basis of null_space includes the basis of stab_space?
    # Galois null_space returns a basis.
    print("Could not find 19th stabilizer easily. Checking combinations...")
    exit(1)

def vec_to_pauli(v):
    s = ""
    n = len(v) // 2
    xs = v[:n]
    zs = v[n:]
    for i in range(n):
        if xs[i] and zs[i]: s += "Y"
        elif xs[i]: s += "X"
        elif zs[i]: s += "Z"
        else: s += "I"
    return s

final_stabs = stabilizers + [vec_to_pauli(found_19th)]

# Now use Stim to generate circuit
stim_stabs = [stim.PauliString(s) for s in final_stabs]

try:
    tableau = stim.Tableau.from_stabilizers(stim_stabs)
    circuit = tableau.to_circuit()
    
    # Circuit puts stabilizers into Z basis?
    # No, to_circuit() implements the tableau unitary U.
    # U maps Z basis to the stabilizers.
    # So U |0> is the state stabilized by the stabilizers.
    # But wait.
    # stim.Tableau.from_stabilizers(S) creates a tableau T such that T(Z_i) = S_i.
    # If we apply the circuit of T to the |0> state, we get the state stabilized by S_i.
    # Why?
    # Because initially the state is stabilized by Z_i.
    # After applying U, the state is stabilized by U Z_i Udagger.
    # By definition of tableau, U Z_i Udagger = S_i.
    # So yes, this works.
    
    # One catch: `from_stabilizers` might fail if they are not valid stabilizers.
    # But we checked commutativity.
    # Also, we need to ensure the signs are +1.
    # stim.Tableau.from_stabilizers takes PauliStrings which include signs.
    # Our strings are like "XXI...", implied +1.
    
    print(circuit)
    
except Exception as e:
    print(f"Error: {e}")
