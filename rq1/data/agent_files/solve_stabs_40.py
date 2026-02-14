import stim
import numpy as np

stabilizers = [
    "XZZXIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIII", "IIIIIXZZXIIIIIIIIIIIIIIIIIIIIIIIIIIIIIII", "IIIIIIIIIIXZZXIIIIIIIIIIIIIIIIIIIIIIIIII", "IIIIIIIIIIIIIIIXZZXIIIIIIIIIIIIIIIIIIIII", "IIIIIIIIIIIIIIIIIIIIXZZXIIIIIIIIIIIIIIII", "IIIIIIIIIIIIIIIIIIIIIIIIIXZZXIIIIIIIIIII", "IIIIIIIIIIIIIIIIIIIIIIIIIIIIIIXZZXIIIIII", "IIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIXZZXI",
    "IXZZXIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIII", "IIIIIIXZZXIIIIIIIIIIIIIIIIIIIIIIIIIIIIII", "IIIIIIIIIIIXZZXIIIIIIIIIIIIIIIIIIIIIIIII", "IIIIIIIIIIIIIIIIXZZXIIIIIIIIIIIIIIIIIIII", "IIIIIIIIIIIIIIIIIIIIIXZZXIIIIIIIIIIIIIII", "IIIIIIIIIIIIIIIIIIIIIIIIIIXZZXIIIIIIIIII", "IIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIXZZXIIIII", "IIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIXZZX",
    "XIXZZIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIII", "IIIIIXIXZZIIIIIIIIIIIIIIIIIIIIIIIIIIIIII", "IIIIIIIIIIXIXZZIIIIIIIIIIIIIIIIIIIIIIIII", "IIIIIIIIIIIIIIIXIXZZIIIIIIIIIIIIIIIIIIII", "IIIIIIIIIIIIIIIIIIIIXIXZZIIIIIIIIIIIIIII", "IIIIIIIIIIIIIIIIIIIIIIIIIXIXZZIIIIIIIIII", "IIIIIIIIIIIIIIIIIIIIIIIIIIIIIIXIXZZIIIII", "IIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIXIXZZ",
    "ZXIXZIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIII", "IIIIIZXIXZIIIIIIIIIIIIIIIIIIIIIIIIIIIIII", "IIIIIIIIIIZXIXZIIIIIIIIIIIIIIIIIIIIIIIII", "IIIIIIIIIIIIIIIZXIXZIIIIIIIIIIIIIIIIIIII", "IIIIIIIIIIIIIIIIIIIIZXIXZIIIIIIIIIIIIIII", "IIIIIIIIIIIIIIIIIIIIIIIIIZXIXZIIIIIIIIII", "IIIIIIIIIIIIIIIIIIIIIIIIIIIIIIZXIXZIIIII", "IIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIZXIXZ",
    "XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX", "ZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZ"
]

num_qubits = 40

class StabilizerTableau:
    def __init__(self, n):
        self.n = n
        self.rows = [] # list of (pivot_index, vector)
        
    def add(self, pauli):
        # Convert to symplectic vector: [x1..xn, z1..zn]
        # x_i=1 if P_i in {X,Y}, z_i=1 if P_i in {Z,Y}
        # But wait, Stim uses specific mapping.
        # Let's just use 0,1 vectors where 1 means it has X or Z component?
        # No, we need 2 bits per qubit.
        # But for independence check over GF(2), we can just treat Pauli group as 2n dimension vector space?
        # Yes, ignoring phases.
        
        vx = np.zeros(self.n, dtype=int)
        vz = np.zeros(self.n, dtype=int)
        
        for i in range(self.n):
            p = pauli[i]
            if p == 1 or p == 2: # X or Y
                vx[i] = 1
            if p == 2 or p == 3: # Y or Z
                vz[i] = 1
                
        vec = np.concatenate((vx, vz))
        
        # Eliminate
        # We need to iterate through existing rows in order of their pivots to ensure we don't re-introduce 1s.
        # So self.rows should be sorted by pivot? Or just iterate?
        # If we iterate by pivot, we are safe.
        
        # Sort rows by pivot just to be safe (though appending in order of discovery works if we always reduce against all previous)
        self.rows.sort(key=lambda x: x[0])
        
        for pivot, r_vec in self.rows:
            if vec[pivot] == 1:
                vec ^= r_vec
                
        # Check if non-zero
        if np.any(vec):
            # Find first non-zero
            pivot = np.where(vec)[0][0]
            self.rows.append((pivot, vec))
            return True
        return False

tracker = StabilizerTableau(num_qubits)
independent_stabilizers = []

print(f"Original count: {len(stabilizers)}")

# Convert strings to PauliStrings
paulis = [stim.PauliString(s) for s in stabilizers]

for p in paulis:
    if tracker.add(p):
        independent_stabilizers.append(p)

print(f"Independent count: {len(independent_stabilizers)}")

# Complete the set
import itertools

if len(independent_stabilizers) < num_qubits:
    print("Completing stabilizer set...")
    # Try adding Z operators on single qubits
    for q in range(num_qubits):
        if len(independent_stabilizers) == num_qubits:
            break
        
        # Try Z
        z_str = ["I"] * num_qubits
        z_str[q] = "Z"
        cand = stim.PauliString("".join(z_str))
        
        # Check commutation
        commutes = True
        for s in independent_stabilizers:
            if not cand.commutes(s):
                commutes = False
                break
        
        if commutes:
            if tracker.add(cand):
                independent_stabilizers.append(cand)
                # print(f"Added Z{q}")
                continue

        # Try X
        x_str = ["I"] * num_qubits
        x_str[q] = "X"
        cand = stim.PauliString("".join(x_str))
        
        commutes = True
        for s in independent_stabilizers:
            if not cand.commutes(s):
                commutes = False
                break
                
        if commutes:
            if tracker.add(cand):
                independent_stabilizers.append(cand)
                # print(f"Added X{q}")

print(f"Final count: {len(independent_stabilizers)}")

if len(independent_stabilizers) == num_qubits:
    tableau = stim.Tableau.from_stabilizers(independent_stabilizers)
    circuit = tableau.to_circuit()
    with open("circuit_attempt.stim", "w") as f:
        f.write(str(circuit))
    print("Circuit written to circuit_attempt.stim")
else:
    print("Could not complete stabilizer set.")
