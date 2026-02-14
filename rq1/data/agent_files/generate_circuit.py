import stim
import numpy as np

# Corrected generators
generators = [
    "IXIIXIIXXXXXIIIIIIIIIIX",
    "XIIXIIXXXXXIIIIIIIIIIXI",
    "IXXIXXXIIIXXIIIIIIIIXII",
    "XXIXXXIIIXXIIIIIIIIXIII",
    "XXXXIIIXIIXXIIIIIIXIIII",  # Fixed
    "XIXIXIXXXIIXIIIIIXIIIII",
    "IIIXXXXIXXIXIIIIXIIIIII",
    "IIXXXXIXXIXIIIIXIIIIIII",
    "IXXXXIXXIXIIIIXIIIIIIII",
    "XXXXIXXIXIIIIXIIIIIIIII",
    "XIXIIXIIXXXXXIIIIIIIIII",
    "IZIIZIIZZZZZIIIIIIIIIIZ",
    "ZIIZIIZZZZZIIIIIIIIIIZI",
    "IZZIZZZIIIZZIIIIIIIIZII",
    "ZZIZZZIIIZZIIIIIIIIZIII",
    "ZZZZIIIZIIZZIIIIIIZIIII",
    "ZIZIZIZZZIIZIIIIIZIIIII",
    "IIIZZZZIZZIZIIIIZIIIIII",
    "IIZZZZIZZIZIIIIZIIIIIII",
    "IZZZZIZZIZIIIIZIIIIIIII",
    "ZZZZIZZIZIIIIZIIIIIIIII",
    "ZIZIIZIIZZZZZIIIIIIIIII"
]

# We need to find a Clifford circuit that maps |0> to the +1 eigenstate of these generators.
# Strategy: Use Tableau algorithm.
# Since we have n=23 and k=22 generators, we have 1 logical qubit.
# We can extend the generator set to 23 by adding a logical operator, or just find any state that satisfies the 22.
# Actually, the simplest way is to use Stim's tableau simulator to find a circuit.
# But Stim doesn't have a "synthesize state preparation circuit" function out of the box that takes strings.
# We can implement Gaussian elimination.

def char_to_pauli(c):
    if c == 'I': return 0
    if c == 'X': return 1
    if c == 'Z': return 3 # Stim uses 1=X, 2=Y, 3=Z
    if c == 'Y': return 2
    return 0

def pauli_to_xz(c):
    if c == 'I': return (0, 0)
    if c == 'X': return (1, 0)
    if c == 'Z': return (0, 1)
    if c == 'Y': return (1, 1)
    return (0, 0)

n = 23
num_gens = len(generators)

# Build the check matrix for the stabilizers
# Matrix size: 22 x (2*n)  (x bits | z bits)
tableau = np.zeros((num_gens, 2*n), dtype=int)

for i, g in enumerate(generators):
    for j, c in enumerate(g):
        x, z = pauli_to_xz(c)
        tableau[i, j] = x
        tableau[i, n+j] = z

# We want to find a Clifford U such that U |0> is stabilized by generators.
# Alternatively, find U such that U P_i U^dagger = Z_i (canonical Z stabilizers).
# Then the circuit is U^dagger acting on |0>.
# Wait, if U P_i U^dagger = Z_i, then P_i = U^dagger Z_i U.
# So if we prepare |0> (stabilized by Z_i) and apply U^dagger, we get state stabilized by P_i.
# So we need to diagonalize the stabilizer group.
# But we only have 22 generators. We can pick a 23rd one Z_23 or something that commutes with all?
# Or just ignore the last qubit in the canonical frame.
# If we map generators G_i to Z_i (for i=0..21), then preparing |00...0> state and applying inverse operations works.
# The 23rd qubit can be in |0> or |+>, it doesn't matter for the first 22 stabilizers?
# Actually, if we map G_i -> Z_i, then Z_i stabilizes |0>.
# So we need to find a sequence of Cliffords that transforms the Tableau of G to the Tableau of Zs (plus maybe some Xs for the logicals).
# The standard algorithm is:
# Gaussian elimination to clear X part, then Z part.
# Operations:
# - CNOT(i, j): adds row i to row j in X block, adds col j to col i in Z block?
# - H(i): swaps X_i and Z_i columns.
# - S(i): adds Z_i to X_i? (X -> Y -> Z -> X)

# Let's write a script to do this Gaussian elimination.

stim_circuit = stim.Circuit()

# We will track the stabilizers as we apply gates.
# Actually, it's easier to track the "destabilizers" and "stabilizers" of the current state
# and map them to the target.
# But here we are given the target stabilizers and want to find the circuit.
# So we start with the target generators, and apply gates to simplify them to single Z's.
# The inverse of those gates (in reverse order) will be the preparation circuit.

# Let's use a full Tableau representation of size 2n x 2n.
# But we only have k=22 stabilizers.
# We can fill the rest with arbitrary valid stabilizers to make a full set of n=23.
# Or just work with the rectangular matrix.

# Let's try to diagonalize the 22x46 matrix.
# We want to transform it to a form where each row is a single Z_i (up to sign).
# Row operations are allowed (multiplying stabilizers).
# Column operations correspond to Clifford gates.
# We record the gates.

# Operations on the tableau (columns 0..n-1 are X, n..2n-1 are Z):
# H(i): swap col i and col n+i.
# S(i): col n+i += col i.
# CX(i, j): col n+i += col n+j; col j += col i.
# SWAP(i, j): swap cols i, j and n+i, n+j.

# After applying gates to simplify the rows to Z_0, Z_1, ..., Z_21,
# The circuit to prepare the state is the INVERSE of the sequence of gates applied.
# And we start with |0...0>.

class StabilizerSolver:
    def __init__(self, gens, n):
        self.n = n
        self.k = len(gens)
        self.table = np.zeros((self.k, 2*n), dtype=int)
        self.phases = np.zeros(self.k, dtype=int) # We might need to track signs, but for now let's assume +1
        # Actually, generators might have signs? The input strings don't have signs.
        # "IX..." implies +IX...
        
        for i, g in enumerate(gens):
            for j, c in enumerate(g):
                x, z = pauli_to_xz(c)
                self.table[i, j] = x
                self.table[i, n+j] = z
                
        self.gates = [] # List of (gate_name, targets)

    def append_gate(self, name, *targets):
        self.gates.append((name, targets))
        # Update table
        if name == 'H':
            i = targets[0]
            self.table[:, [i, self.n+i]] = self.table[:, [self.n+i, i]]
        elif name == 'S':
            i = targets[0]
            # S maps X -> Y = XZ, Z -> Z.
            # In tableau (x, z): X=(1,0) -> (1,1), Z=(0,1) -> (0,1).
            # So z += x.
            self.table[:, self.n+i] ^= self.table[:, i]
        elif name == 'CX':
            c, t = targets
            # CX maps:
            # X_c -> X_c X_t : (1,0)_c, (0,0)_t -> (1,0)_c, (1,0)_t
            # Z_c -> Z_c     : (0,1)_c, (0,0)_t -> (0,1)_c, (0,0)_t
            # X_t -> X_t     : (0,0)_c, (1,0)_t -> (0,0)_c, (1,0)_t
            # Z_t -> Z_c Z_t : (0,0)_c, (0,1)_t -> (0,1)_c, (0,1)_t
            
            # Update columns:
            # col x_t += col x_c
            # col z_c += col z_t
            self.table[:, t] ^= self.table[:, c]
            self.table[:, self.n+c] ^= self.table[:, self.n+t]

    def solve(self):
        # Gaussian elimination to reduce to single Z's.
        # We want rows to look like Z_0, Z_1, ...
        # i.e. X part is 0, Z part is identity (or permutation).
        
        current_row = 0
        
        # Eliminate X components
        for col in range(self.n):
            if current_row >= self.k: break
            
            # Find a row with X at 'col'
            pivot = -1
            for r in range(current_row, self.k):
                if self.table[r, col] == 1:
                    pivot = r
                    break
            
            if pivot != -1:
                # Swap pivot to current_row
                if pivot != current_row:
                    self.table[[current_row, pivot]] = self.table[[pivot, current_row]]
                
                # Use H to swap X and Z? No, we want to eliminate X to get Z.
                # If we have X, we can convert it to Z with H.
                # But typically we want to clear X components first using CNOTs?
                # Wait, standard form for stabilizer state is X...X (destabilizers) / Z...Z (stabilizers).
                # We want to map our stabilizers to Z_i.
                # So we want to transform the table so that X part is 0.
                
                # Found an X at (current_row, col).
                # Apply Hadamard at 'col' to turn it into Z?
                # If we do H(col), X_col becomes Z_col.
                # But we want to preserve the structure?
                # Actually, simply clearing X is good.
                # If we have X, we can use CNOTs to clear other X's in the column.
                
                # Strategy:
                # 1. Ensure we have a pivot with X=1.
                # 2. Use CNOTs to clear X in other rows at this column.
                # 3. Apply H to convert this X to Z? Or just leave it as X and later convert?
                # Let's try to make the tableau into [I | 0] (X stabilizers) or [0 | I] (Z stabilizers).
                # Since we want to prepare |0>, we want the stabilizers to be Z_i.
                # So we want to map the current stabilizers to Z-basis.
                
                # If we find X, apply H to make it Z.
                self.append_gate('H', col)
                
                # Now the pivot has Z=1 at 'col' (and X=0).
                # Wait, if it had Z=1 before, now it has X=1.
                # Let's check what happened.
                # We found X=1. Applied H -> now X=0, Z=1.
                # But if it had Z=1 too (Y), then now it has X=1, Z=0? No.
                # Y = (1,1). H maps Y -> -Y = (1,1).
                # So H doesn't help if it was Y.
                
                # Let's stick to clearing columns.
                # For column 'col', we want to pick a pivot.
                # Preferably one with X=1.
                
                # If we have X=1, we can use it to eliminate other X's in the column using CNOTs?
                # CNOT(c, t) adds X_c to X_t.
                # So if pivot is 'c', we can target other 't' to zero them.
                
                # Let's refine the strategy.
                # Goal: Reduce to row-echelon form for X part.
                pass 
                
        # This is getting complicated to implement from scratch.
        # Alternative: Graph state approach.
        # But graph state needs finding the adjacency matrix.
        # Let's use the provided hint: "Gaussian elimination on the stabilizer tableau".
        
        # Let's retry the strategy:
        # We want to map generators G_i to Z_i.
        # Iterate i from 0 to k-1.
        # We want G_i to become Z_i.
        # And G_j (j > i) to not involve qubit i (or at least be cleaned up).
        
        for i in range(self.k):
            # We want to make the i-th generator equal to Z_i (on qubit i).
            # And clear qubit i from all other generators.
            
            # Step 1: Find a generator that has non-commuting Pauli on qubit i?
            # Or just any Pauli?
            # We want G_i to be Z_i eventually.
            # So we need a generator that has X_i or Z_i or Y_i.
            
            # Search for a pivot in rows i..k-1 at qubit i.
            # We prefer X or Y component to be present? 
            # Actually, we can swap columns (qubits) if needed, but we can't re-index qubits (physically).
            # We can only use local Cliffords.
            
            # Check if any row j>=i has non-identity on qubit i.
            pivot = -1
            p_type = None
            for r in range(i, self.k):
                x = self.table[r, i]
                z = self.table[r, self.n+i]
                if x == 1 and z == 1: # Y
                    pivot = r; p_type = 'Y'; break
                if x == 1: # X
                    pivot = r; p_type = 'X'; break
                if z == 1: # Z
                    pivot = r; p_type = 'Z'; break
            
            if pivot == -1:
                # No generator acts on qubit i.
                # This is a problem if we want to map to Z_i.
                # It implies qubit i is not involved in the remaining stabilizers?
                # We can skip this qubit and move to next?
                # But we have 22 generators and 23 qubits.
                # Maybe we map to Z_{p(i)}?
                continue
                
            # Swap pivot to row i
            if pivot != i:
                self.table[[i, pivot]] = self.table[[pivot, i]]
                
            # Now G_i has Pauli P on qubit i.
            # Transform P to X_i using local Cliffords.
            x = self.table[i, i]
            z = self.table[i, self.n+i]
            
            if x == 1 and z == 1: # Y
                # Sdag H S? Or just S H?
                # S maps X->Y. Sdag maps Y->X.
                # Apply Sdag(i).
                # In our set, we can use S, H. S^3 = Sdag.
                self.append_gate('S', i)
                self.append_gate('S', i)
                self.append_gate('S', i)
                # Now it should be X.
            elif x == 0 and z == 1: # Z
                # H maps Z -> X
                self.append_gate('H', i)
                # Now it should be X.
            elif x == 1 and z == 0: # X
                pass # Already X
            
            # Now G_i has X on qubit i.
            # Use this X to eliminate X on qubit i from other rows j != i.
            # Use CNOT(i, j) ? No, CNOT target updates X.
            # If we do CNOT(i, k), X_i propagates to X_k.
            # We want to eliminate X_i in other rows?
            # No, we want to eliminate X/Z on qubit i from other rows using G_i.
            # But we can only apply unitary gates.
            # We can't "subtract rows". Row operations are just re-choosing generators (classical).
            # We CAN do row operations! The stabilizer group is preserved under multiplication.
            
            # So:
            # 1. Make G_i have X on qubit i (using gates).
            # 2. Use row multiplication to remove X on qubit i from all other G_j (j != i).
            #    If G_j has X on i, G_j = G_j * G_i.
            # 3. Now G_i is the unique generator with X on i.
            #    Wait, what about Z on i?
            #    Since all generators commute, and G_i has X on i,
            #    any other G_j must commute with X_i.
            #    So G_j must have I or X on qubit i. It cannot have Z or Y (anticommute).
            #    So clearing X is enough!
            
            # Perform row reduction for X column i
            for r in range(self.k):
                if r == i: continue
                if self.table[r, i] == 1: # Has X (and thus matches G_i on this qubit)
                    self.table[r, :] ^= self.table[i, :]
            
            # Now G_i has X_i, and all other G_j have I_i.
            # Finally, apply Hadamard on i to convert X_i to Z_i.
            self.append_gate('H', i)
            # Now G_i is Z_i... (and possibly other stuff on j > i).
            # All other G_j have I on i.
            
            # Move to next qubit/generator.
            
        return self.gates

solver = StabilizerSolver(generators, 23)
gates = solver.solve()

# The preparation circuit is the INVERSE of the gates applied, applied to |0>.
# The solver gates map G_target -> Z_basis.
# So U |psi> = |0>. => |psi> = U^dagger |0>.
# We need to apply gates in reverse order, inverted.
# H is self-inverse. CX is self-inverse. S inverse is S^3.

print("circuit = stim.Circuit()")
for name, targets in reversed(gates):
    if name == 'H':
        print(f"circuit.append('H', {targets})")
    elif name == 'CX':
        print(f"circuit.append('CX', {targets})")
    elif name == 'S':
        # Inverse of S is S_DAG
        print(f"circuit.append('S_DAG', {targets})")

