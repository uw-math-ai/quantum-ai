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
                
        self.gates = [] 

    def append_gate(self, name, *targets):
        # We append gates to the list. These are gates applied to the generators
        # to simplify them. The preparation circuit is the inverse of these gates.
        self.gates.append((name, targets))
        
        if name == 'H':
            i = targets[0]
            self.table[:, [i, self.n+i]] = self.table[:, [self.n+i, i]]
        elif name == 'S':
            i = targets[0]
            # S: Z -> Z, X -> Y=XZ.
            # In (x,z) form: (1,0)->(1,1), (0,1)->(0,1).
            # z += x
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
            self.table[:, self.n+c] ^= self.table[:, t]
            self.table[:, self.n+t] ^= self.table[:, c]
        elif name == 'SWAP':
             a, b = targets
             # Swap columns a and b for X and Z
             self.table[:, [a, b]] = self.table[:, [b, a]]
             self.table[:, [self.n+a, self.n+b]] = self.table[:, [self.n+b, self.n+a]]

    def solve(self):
        current_qubit = 0
        
        for r in range(self.k):
            # 1. Find pivot row >= r with Pauli X or Y on qubit >= current_qubit
            # Prefer X on current_qubit
            
            pivot = -1
            pivot_q = -1
            
            # Priority 1: X on current_qubit
            for row in range(r, self.k):
                if self.table[row, current_qubit] == 1:
                    pivot = row
                    pivot_q = current_qubit
                    break
            
            # Priority 2: Z (or Y) on current_qubit
            if pivot == -1:
                for row in range(r, self.k):
                    if self.table[row, self.n+current_qubit] == 1:
                        pivot = row
                        pivot_q = current_qubit
                        break
            
            # Priority 3: X on later qubits
            if pivot == -1:
                for q in range(current_qubit + 1, self.n):
                    for row in range(r, self.k):
                        if self.table[row, q] == 1:
                            pivot = row
                            pivot_q = q
                            break
                    if pivot != -1: break
            
            # Priority 4: Z on later qubits
            if pivot == -1:
                for q in range(current_qubit + 1, self.n):
                    for row in range(r, self.k):
                        if self.table[row, self.n+q] == 1:
                            pivot = row
                            pivot_q = q
                            break
                    if pivot != -1: break
            
            if pivot == -1:
                break # Done or dependent rows
                
            # Bring pivot row to r
            if pivot != r:
                self.table[[r, pivot]] = self.table[[pivot, r]]
                
            # Bring pivot qubit to current_qubit
            if pivot_q != current_qubit:
                self.append_gate('SWAP', current_qubit, pivot_q)
            
            q = current_qubit
            
            # Make G_r have X_q
            x = self.table[r, q]
            z = self.table[r, self.n+q]
            
            if x == 1 and z == 1: # Y
                self.append_gate('S', q); self.append_gate('S', q); self.append_gate('S', q) # Sdag
            elif x == 0 and z == 1: # Z
                self.append_gate('H', q)
            
            # Now G_r starts with X_q ...
            # 2. Eliminate X_q from other rows j != r
            for j in range(self.k):
                if j != r and self.table[j, q] == 1:
                    self.table[j, :] ^= self.table[r, :]
                    
            # 3. Eliminate Pauli on q+1..n-1 from G_r using CNOTs/CZs controlled by q
            # Because G_r has X_q, we can use it to control operations.
            # We want G_r to be just X_q (so we can swap it to Z_q later and be done).
            
            for target_q in range(q + 1, self.n):
                # If G_r has X_{target_q}, apply CNOT(q, target_q)
                # X_q -> X_q X_{target_q}
                # So it adds X_{target_q} to the generator.
                # If generator already has X_{target_q}, it cancels it (1+1=0).
                if self.table[r, target_q] == 1:
                    self.append_gate('CX', q, target_q)
                
                # If G_r has Z_{target_q}, apply CZ(q, target_q)
                # X_q -> X_q Z_{target_q}
                if self.table[r, self.n+target_q] == 1:
                    self.append_gate('CZ', q, target_q)
                    
            # Now G_r should be exactly X_q (and I elsewhere).
            # Verify?
            # if np.any(self.table[r, q+1:]) or np.any(self.table[r, self.n+q+1:]):
            #     print(f"Warning: row {r} not cleared properly")
            
            # 4. Finally, convert G_r (which is X_q) to Z_q.
            self.append_gate('H', q)
            
            # Now G_r is Z_q.
            # Eliminate Z_q from other rows j != r.
            # We can just multiply rows.
            for j in range(self.k):
                if j != r and self.table[j, self.n+q] == 1:
                    self.table[j, :] ^= self.table[r, :]
            
            current_qubit += 1
            
        return self.gates

solver = StabilizerSolver(generators, 23)
gates = solver.solve()

# Inverse circuit
# print("circuit = stim.Circuit()")
full_circuit = stim.Circuit()
for name, targets in reversed(gates):
    # t_str = ", ".join(str(t) for t in targets)
    # Correct handling for Stim batch commands
    # Stim commands like CX take pairs. If we have multiple CX with same control, we should issue separate commands
    # or ensure they don't overlap in a way that implies parallel execution if Stim assumes distinct pairs.
    # Stim's `CX 0 1 0 2` is INVALID because qubit 0 is used twice in the same instruction line.
    # We must split them.
    
    if name in ['CX', 'CZ', 'SWAP']:
        # These are 2-qubit gates. Targets is (c, t).
        # My append_gate only appends one pair at a time.
        # So targets is just (c, t).
        # Oh, wait. My append_gate takes *targets.
        # In solve(), I call self.append_gate('CX', q, target_q).
        # So targets is (q, target_q).
        # So each entry in gates is a single operation.
        
        full_circuit.append(name, targets)
        
    elif name in ['H', 'S']:
        # Single qubit gates.
        full_circuit.append(name, targets)
        
print(full_circuit)
