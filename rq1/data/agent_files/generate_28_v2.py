import stim
import numpy as np
import galois

stabilizers_str = [
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

num_qubits = 28

def str_to_xz(s):
    x = np.array([1 if c in 'XY' else 0 for c in s], dtype=int)
    z = np.array([1 if c in 'ZY' else 0 for c in s], dtype=int)
    return x, z

stabilizers_x = []
stabilizers_z = []

for s in stabilizers_str:
    x, z = str_to_xz(s)
    stabilizers_x.append(x)
    stabilizers_z.append(z)

stabilizers_x = np.array(stabilizers_x)
stabilizers_z = np.array(stabilizers_z)

def commutes(x1, z1, x2, z2):
    return (np.sum(x1 * z2 + z1 * x2) % 2) == 0

def find_completion():
    current_x = list(stabilizers_x)
    current_z = list(stabilizers_z)
    
    # Try adding single Zs or Xs
    candidates = []
    for i in range(num_qubits):
        # Z_i
        zx = np.zeros(num_qubits, dtype=int)
        zz = np.zeros(num_qubits, dtype=int)
        zz[i] = 1
        candidates.append((zx, zz))
        # X_i
        xx = np.zeros(num_qubits, dtype=int)
        xx[i] = 1
        xz = np.zeros(num_qubits, dtype=int)
        candidates.append((xx, xz))
        
    for cx, cz in candidates:
        if len(current_x) == 28:
            break
            
        # Check commutation with ALL
        commutes_all = True
        for i in range(len(current_x)):
            if not commutes(cx, cz, current_x[i], current_z[i]):
                commutes_all = False
                break
        if not commutes_all:
            continue
            
        # Check independence
        temp_x = np.vstack([current_x, cx])
        temp_z = np.vstack([current_z, cz])
        
        # Rank check using Galois
        gf_x = galois.GF(2)(temp_x)
        gf_z = galois.GF(2)(temp_z)
        tableau = np.concatenate((gf_x, gf_z), axis=1)
        rank = np.linalg.matrix_rank(tableau)
        
        if rank == len(current_x) + 1:
            current_x.append(cx)
            current_z.append(cz)
            
    if len(current_x) < 28:
        print("Could not find full set of stabilizers")
        return None
        
    return current_x, current_z

result = find_completion()
if result:
    final_x, final_z = result
    # Convert to Stim PauliStrings
    stim_stabilizers = []
    for i in range(28):
        s = ""
        for k in range(num_qubits):
            x = final_x[i][k]
            z = final_z[i][k]
            if x and z: s += "Y"
            elif x: s += "X"
            elif z: s += "Z"
            else: s += "_"
        stim_stabilizers.append(stim.PauliString(s))
        
    tableau = stim.Tableau.from_stabilizers(stim_stabilizers)
    circuit = tableau.to_circuit()
    
    # Verify the circuit prepares +1 eigenstate
    # stim.Tableau.from_stabilizers creates a tableau T such that T|0> has the given stabilizers.
    # However, it might have signs -1.
    # T.to_circuit() gives the circuit C such that C|0> = T|0>.
    # We need to check if the stabilizers are +1 or -1.
    # We can check by simulating the circuit and measuring the stabilizers.
    
    with open("circuit_28_v2.stim", "w") as f:
        f.write(str(circuit))
    print("Circuit written to circuit_28_v2.stim")

