import stim
import numpy as np

stabilizers = [
    "IIIIXIIIIIXIIIXIXIXIIIIIXIIIIIIIIIIII",
    "IIIIIXIIIIIIXIIXIIIXIIIIIIIIIIIIIIIII",
    "IIIIIIIIIIIIIIIIIXIIXXIIIIIIIIIXIIIII",
    "IIIIIIIIIIIIIIIIIIIIIIXIIXIIIIIIIIIXX",
    "IIIXIIIIIIIIIIIIIIIIIIXXIIXIIXIIIIIIX",
    "XIIIIIXIIIIIIIIIIIIIIIIIIIIIIIIIXXIII",
    "IIIIIIIIIXIIIIIXIIIXIIIIIIIIXIIIIIIII",
    "XIIIIIIIIIIIIIIIXIIIIIIIXIXIIXIIXIIII",
    "IXXIIIIIIIIIIIIIIIIIIIIIIIIXIIXIIIIII",
    "IXXIIIIXXIIXIIIIIIIIIIIIIIIIIIIIIIXII",
    "IIIIXIIIXIIIIIXIIIIIIIIIIIIIIIIIIIXII",
    "IIIIIIIIIIXIIIIIIXXIIXIIIIIIIIIIIIIII",
    "XIIXIXXIIIIIXIIIIIIIIIIIIIIIIXIIIIIII",
    "IIXIIIIIIIIXIXIIIIIIIIIIIIIIIIXIIIIII",
    "IIIIIIIXIIIXIXIIIIIIIIXXIXIIIIIIIIIII",
    "IIIIIIIXXIIIIIXIXIIIIIIXIIXIIIIIIIIII",
    "IIIIIIIIIIIIIIIIIIXIIXIIXIIIIIIXXXIII",
    "IIIXIXIIIXIIIIIXIIIIIIIIIIIIIIIIIIIXX",
    "IIIIZIIIIIZIIIZIZIZIIIIIZIIIIIIIIIIII",
    "IIIIIZIIIIIIZIIZIIIZIIIIIIIIIIIIIIIII",
    "IIIIIIIIIIIIIIIIIZIIZZIIIIIIIIIZIIIII",
    "IIIIIIIIIIIIIIIIIIIIIIZIIZIIIIIIIIIZZ",
    "IIIZIIIIIIIIIIIIIIIIIIZZIIZIIZIIIIIIZ",
    "ZIIIIIZIIIIIIIIIIIIIIIIIIIIIIIIIZZIII",
    "IIIIIIIIIZIIIIIZIIIZIIIIIIIIZIIIIIIII",
    "ZIIIIIIIIIIIIIIIZIIIIIIIZIZIIZIIZIIII",
    "IZZIIIIIIIIIIIIIIIIIIIIIIIIZIIZIIIIII",
    "IZZIIIIZZIIZIIIIIIIIIIIIIIIIIIIIIIZII",
    "IIIIZIIIZIIIIIZIIIIIIIIIIIIIIIIIIIZII",
    "IIIIIIIIIIZIIIIIIZZIIZIIIIIIIIIIIIIII",
    "ZIIZIZZIIIIIZIIIIIIIIIIIIIIIIZIIIIIII",
    "IIZIIIIIIIIZIZIIIIIIIIIIIIIIIIZIIIIII",
    "IIIIIIIZIIIZIZIIIIIIIIZZIZIIIIIIIIIII",
    "IIIIIIIZZIIIIIZIZIIIIIIZIIZIIIIIIIIII",
    "IIIIIIIIIIIIIIIIIIZIIZIIZIIIIIIZZZIII",
    "IIIZIZIIIZIIIIIZIIIIIIIIIIIIIIIIIIIZZ"
]

print(f"Stim version: {stim.__version__}")
try:
    print(f"Tableau.from_stabilizers exists: {hasattr(stim.Tableau, 'from_stabilizers')}")
except:
    print("Tableau.from_stabilizers check failed")

# Check commutation
paulis = [stim.PauliString(s) for s in stabilizers]
commutes = True
for i in range(len(paulis)):
    for j in range(i+1, len(paulis)):
        if not paulis[i].commutes(paulis[j]):
            print(f"Non-commuting at {i}, {j}")
            commutes = False
            break
    if not commutes: break

if commutes:
    print("All stabilizers commute.")
else:
    print("Stabilizers do NOT commute.")

# Try to find the 37th stabilizer
if commutes:
    # Convert to binary matrix
    # shape (36, 74)
    # columns: x0, z0, x1, z1 ...
    mat = []
    for p in paulis:
        row = []
        for k in range(37):
            # 0: I, 1: X, 2: Y, 3: Z
            # But here we want symplectic form
            # x_k, z_k
            op = p[k]
            if op == 0: # I
                row.extend([0, 0])
            elif op == 1: # X
                row.extend([1, 0])
            elif op == 2: # Y
                row.extend([1, 1])
            elif op == 3: # Z
                row.extend([0, 1])
        mat.append(row)
    
    # We want to find a vector v such that M @ v^T = 0 (mod 2) (commutation)
    # And v is independent of rows of M.
    # The symplectic inner product is v @ Omega @ w^T
    # Here let's just use stim's internal tools if possible, but calculating null space manually is safer.
    
    # Let's rely on finding a logical operator.
    # Since we have 36 stabilizers on 37 qubits, there is 1 logical qubit.
    # The logical operators L_X, L_Z will commute with all stabilizers.
    # We just need to find one such operator that is not in the stabilizer group.
    
    print("Ready to solve.")
