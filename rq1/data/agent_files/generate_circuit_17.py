import stim
import numpy as np
from ldpc import mod2

# Generators provided
x_gens = [
    "IIIIIXIIIXIXXIIII",
    "IIIIIIIIXIXIIXIXI",
    "IIIXIIIXIIIIIIXIX",
    "IIXIIIXIIIIIIIXIX",
    "IIIIXXXXXIXXIIIIX",
    "IXIIXIIIIIXIIXIII",
    "IIIIIIIIXXIXIIIXI",
    "XIXXIIIIIIIIIIXII"
]

z_gens = [
    "IIIIIZIIIZIZZIIII",
    "IIIIIIIIZIZIIZIZI",
    "IIIZIIIZIIIIIIZIZ",
    "IIZIIIZIIIIIIIZIZ",
    "IIIIZZZZZIZZIIIIZ",
    "IZIIZIIIIIZIIZIII",
    "IIIIIIIIZZIZIIIZI",
    "ZIZZIIIIIIIIIIZII"
]

n_qubits = 17

def to_binary(gens, type_char):
    mat = []
    for g in gens:
        row = [1 if c == type_char else 0 for c in g]
        mat.append(row)
    return np.array(mat, dtype=int)

Hx = to_binary(x_gens, 'X')
Hz = to_binary(z_gens, 'Z')

ker_Hx = mod2.nullspace(Hx)
# Check if sparse and convert
if hasattr(ker_Hx, "toarray"):
    ker_Hx = ker_Hx.toarray()

ker_Hz = mod2.nullspace(Hz)
if hasattr(ker_Hz, "toarray"):
    ker_Hz = ker_Hz.toarray()

def get_independent_vector(basis, target_vecs):
    current_basis = basis.copy()
    for v in target_vecs:
        test_mat = np.vstack([current_basis, v])
        if mod2.rank(test_mat) > mod2.rank(current_basis):
            return v
    return None

z_l_vec = get_independent_vector(Hz, ker_Hx)
if z_l_vec is None:
    print("Could not find Z_L")
    exit(1)

z_l_str = ""
for i in range(n_qubits):
    z_l_str += "Z" if z_l_vec[i] else "I"

full_stabilizers = []
for g in x_gens:
    full_stabilizers.append(stim.PauliString(g))
for g in z_gens:
    full_stabilizers.append(stim.PauliString(g))
full_stabilizers.append(stim.PauliString(z_l_str))

print(f"Total stabilizers: {len(full_stabilizers)}")

try:
    # stim.Tableau.from_stabilizers(stabilizers, allow_redundant=False, allow_underconstrained=False)
    # Note: `from_stabilizers` was added recently. If not available, we need another way.
    tableau = stim.Tableau.from_stabilizers(full_stabilizers)
    print("Tableau created.")
    
    circuit = tableau.to_circuit()
    with open("circuit_17.stim", "w") as f:
        f.write(str(circuit))
    print("Circuit saved to circuit_17.stim")

except AttributeError:
    print("stim.Tableau.from_stabilizers not found. Attempting manual construction.")
    # If unavailable, we can construct the tableau column by column? No too hard.
    # But wait, if we have full stabilizers, we have a unique state.
    # We can use Gaussian elimination.
    # Start with identity tableau (Z-stabilizers Z0..Z16, X-destabilizers X0..X16).
    # We want to reach a state with Z-stabilizers given by full_stabilizers.
    # Actually, stim.Tableau.from_stabilizers does exactly this.
    # If it's missing, I can try to use a newer version of stim if possible, or use a workaround.
    pass
except Exception as e:
    print(f"Error: {e}")
