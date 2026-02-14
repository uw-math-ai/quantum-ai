import stim
import numpy as np

# Corrected generators
generators = [
    "IXIIXIIXXXXXIIIIIIIIIIX",
    "XIIXIIXXXXXIIIIIIIIIIXI",
    "IXXIXXXIIIXXIIIIIIIIXII",
    "XXIXXXIIIXXIIIIIIIIXIII",
    "XXXXIIIXIIXXIIIIIIXIIII",
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

def pauli_to_xz(c):
    if c == 'I': return (0, 0)
    if c == 'X': return (1, 0)
    if c == 'Z': return (0, 1)
    if c == 'Y': return (1, 1)
    return (0, 0)

class StabilizerSolver:
    def __init__(self, gens, n):
        self.n = n
        self.k = len(gens)
        self.table = np.zeros((self.k, 2*n), dtype=int)
        
        for i, g in enumerate(gens):
            for j, c in enumerate(g):
                x, z = pauli_to_xz(c)
                self.table[i, j] = x
                self.table[i, n+j] = z
                
        self.gates = [] # List of (gate_name, targets)

    def append_gate(self, name, *targets):
        self.gates.append((name, targets))
        if name == 'H':
            i = targets[0]
            # Swap X and Z columns
            self.table[:, [i, self.n+i]] = self.table[:, [self.n+i, i]]
        elif name == 'S':
            i = targets[0]
            # Z += X
            self.table[:, self.n+i] ^= self.table[:, i]
        elif name == 'CX':
            c, t = targets
            # X_t += X_c
            # Z_c += Z_t
            self.table[:, t] ^= self.table[:, c]
            self.table[:, self.n+c] ^= self.table[:, self.n+t]
        elif name == 'CZ':
            c, t = targets
            # Z_c += X_t
            # Z_t += X_c
            # Check: CZ |x,z> = |x, z + x_other>
            # X_c -> X_c Z_t : (1,0)_c (0,0)_t -> (1,0)_c (0,1)_t
            # Z_c -> Z_c     : (0,1)_c (0,0)_t -> (0,1)_c (0,0)_t
            # So Z column updates.
            self.table[:, self.n+c] ^= self.table[:, t]
            self.table[:, self.n+t] ^= self.table[:, c]

    def solve(self):
        # Gaussian elimination
        # Goal: Reduce tableau to [0 | I] (Z-basis stabilizers) on first k qubits
        # Actually, we can reduce to [0 | I] on ANY k qubits.
        
        # We process each generator i from 0 to k-1.
        # We want to map G_i to Z_i.
        
        current_qubit = 0
        
        for r in range(self.k):
            # Find a pivot in rows r..k-1 at current_qubit or later
            pivot = -1
            pivot_q = -1
            
            # Search for X or Y (anti-commutes with Z) to serve as X-part
            # Or Z (commutes with Z) to serve as Z-part.
            # We want to transform G_r to Z_{current_qubit}.
            # So we need a pivot that has non-trivial Pauli on some qubit q >= current_qubit.
            
            # Strategy:
            # 1. Clear X components first?
            # No, let's just make the diagonal element X_i = 1.
            # Search for row with X=1.
            
            found = False
            for q in range(current_qubit, self.n):
                for row in range(r, self.k):
                    if self.table[row, q] == 1:
                        pivot = row
                        pivot_q = q
                        found = True
                        break
                if found: break
            
            if not found:
                # No X component found in remaining rows/qubits?
                # Try Z component.
                for q in range(current_qubit, self.n):
                    for row in range(r, self.k):
                        if self.table[row, self.n+q] == 1:
                            pivot = row
                            pivot_q = q
                            found = True
                            break
                    if found: break
            
            if not found:
                # Remaining generators are Identity? Should not happen if independent.
                break
                
            # Swap row pivot to r
            if pivot != r:
                self.table[[r, pivot]] = self.table[[pivot, r]]
                
            # Swap qubit pivot_q to current_qubit?
            # We cannot physically swap qubits easily (requires SWAP gates).
            # But we can SWAP gates.
            if pivot_q != current_qubit:
                # Apply SWAP(current_qubit, pivot_q)
                # We can implement SWAP using 3 CNOTs or just logical swap.
                # Let's use 3 CNOTs: CX(a,b) CX(b,a) CX(a,b)
                a, b = current_qubit, pivot_q
                self.append_gate('CX', a, b)
                self.append_gate('CX', b, a)
                self.append_gate('CX', a, b)
                # Now the pivot is at current_qubit.
            
            q = current_qubit
            
            # Now G_r has non-trivial Pauli at q.
            # Make it X_q.
            x = self.table[r, q]
            z = self.table[r, self.n+q]
            
            if x == 1 and z == 1: # Y
                # Sdag maps Y -> X
                self.append_gate('S', q)
                self.append_gate('S', q)
                self.append_gate('S', q)
            elif x == 0 and z == 1: # Z
                # H maps Z -> X
                self.append_gate('H', q)
            elif x == 0 and z == 0:
                # Should not happen as we found pivot
                pass
                
            # Now G_r has X_q = 1.
            # Eliminate X_q from other rows j != r
            # Use row operations (classical).
            for j in range(self.k):
                if j != r and self.table[j, q] == 1:
                    self.table[j, :] ^= self.table[r, :]
            
            # Now G_r is the only one with X_q.
            # What about Z_q?
            # Since all generators commute, and G_r has X_q (and maybe other stuff),
            # any G_j must commute with G_r.
            # Commutativity on qubit q: [X, ?].
            # If G_j has I_q, it commutes.
            # If G_j has X_q, it commutes. (But we eliminated X_q).
            # If G_j has Z_q or Y_q, it anti-commutes.
            # Since G_j has X_q = 0 (I or Z), it must be I or Z.
            # If it is Z, it anti-commutes with X.
            # For G_j to commute with G_r, the total anti-commutativity must be even.
            # So if G_j has Z_q, it must anti-commute elsewhere.
            
            # We want to clear Z_q from G_r as well?
            # X_q Z_q = Y_q? No, we have (1, 1) = Y in table.
            # But we made sure we have X (1, 0) or Y (1, 1).
            # If we had Y, we converted to X. So now Z_q should be 0.
            # Let's check:
            # If Y (1,1) -> Sdag -> X (1,0). Correct.
            # If Z (0,1) -> H -> X (1,0). Correct.
            # If X (1,0) -> X (1,0). Correct.
            
            # So G_r has X_q (1,0).
            # Other G_j have X_q = 0.
            # Can G_j have Z_q?
            # If G_j has Z_q, it anti-commutes with G_r at q.
            # So it must anti-commute elsewhere.
            # We can use CNOTs/CZs to move that anti-commutativity?
            
            # Actually, standard algorithm:
            # 1. Gaussian elimination X.
            # 2. Gaussian elimination Z.
            
            # We have cleared X_q for all j != r.
            # Now convert G_r to Z_q.
            # Apply H(q). X_q -> Z_q.
            self.append_gate('H', q)
            
            # Now G_r has Z_q.
            # Eliminate Z_q from other rows j != r?
            # Since G_r has Z_q, if G_j has Z_q, we can multiply G_j *= G_r.
            for j in range(self.k):
                if j != r and self.table[j, self.n+q] == 1:
                    self.table[j, :] ^= self.table[r, :]
            
            # Now G_r is Z_q (and other stuff on q+1..n).
            # G_j (j!=r) has I_q.
            
            current_qubit += 1

        return self.gates

solver = StabilizerSolver(generators, 23)
gates = solver.solve()

print("circuit = stim.Circuit()")
for name, targets in reversed(gates):
    t_str = ", ".join(str(t) for t in targets)
    if name == 'H':
        print(f"circuit.append('H', [{t_str}])")
    elif name == 'CX':
        # CX takes targets as [control, target]
        print(f"circuit.append('CX', [{t_str}])")
    elif name == 'S':
        print(f"circuit.append('S_DAG', [{t_str}])")
