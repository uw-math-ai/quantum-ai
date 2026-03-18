import stim
import numpy as np
import sys

def check_circuit(circuit, stabilizers):
    sim = stim.TableauSimulator()
    sim.do(circuit)
    for s in stabilizers:
        if sim.peek_observable_expectation(s) != 1:
            return False
    return True

class GraphStateOptimizer:
    def __init__(self, stabilizers_file):
        with open(stabilizers_file, "r") as f:
            lines = [l.strip() for l in f if l.strip()]
        self.stabilizers = [stim.PauliString(s) for s in lines]
        self.num_qubits = len(self.stabilizers[0])
        self.num_stab = len(self.stabilizers)
        
        self.U = stim.Tableau(self.num_qubits)
        
        self.matrix = np.zeros((self.num_stab, 2*self.num_qubits), dtype=bool)
        for i, s in enumerate(self.stabilizers):
            for k in range(self.num_qubits):
                p = s[k]
                if p == 1 or p == 2: # X or Y
                    self.matrix[i, k] = 1
                if p == 3 or p == 2: # Z or Y
                    self.matrix[i, k + self.num_qubits] = 1

    def apply_H(self, k):
        self.U.append(stim.Tableau.from_named_gate("H"), [k])
        self.matrix[:, [k, k+self.num_qubits]] = self.matrix[:, [k+self.num_qubits, k]]

    def apply_S(self, k):
        self.U.append(stim.Tableau.from_named_gate("S"), [k])
        x_col = self.matrix[:, k]
        z_col = self.matrix[:, k + self.num_qubits]
        self.matrix[:, k + self.num_qubits] = z_col ^ x_col

    def apply_S_dag(self, k):
        self.U.append(stim.Tableau.from_named_gate("S_DAG"), [k])
        x_col = self.matrix[:, k]
        z_col = self.matrix[:, k + self.num_qubits]
        self.matrix[:, k + self.num_qubits] = z_col ^ x_col

    def row_mult(self, i, j):
        self.matrix[j, :] ^= self.matrix[i, :]

    def diagonalize(self):
        print("Diagonalizing...")
        pivot_row = 0
        self.pivots = {} # col -> row
        
        for k in range(self.num_qubits):
            if pivot_row >= self.num_stab:
                break
                
            found = False
            for r in range(pivot_row, self.num_stab):
                if self.matrix[r, k]:
                    if r != pivot_row:
                        self.matrix[[pivot_row, r]] = self.matrix[[r, pivot_row]]
                    found = True
                    break
            
            if not found:
                has_z = False
                for r in range(pivot_row, self.num_stab):
                    if self.matrix[r, k + self.num_qubits]:
                        has_z = True
                        break
                
                if has_z:
                    self.apply_H(k)
                    for r in range(pivot_row, self.num_stab):
                        if self.matrix[r, k]:
                            if r != pivot_row:
                                self.matrix[[pivot_row, r]] = self.matrix[[r, pivot_row]]
                            found = True
                            break
            
            if found:
                for r in range(self.num_stab):
                    if r != pivot_row and self.matrix[r, k]:
                        self.row_mult(pivot_row, r)
                self.pivots[k] = pivot_row
                pivot_row += 1
            else:
                pass

        # Fix Y -> X
        for k in self.pivots:
            r = self.pivots[k]
            if self.matrix[r, k + self.num_qubits]:
                self.apply_S_dag(k)
        
        # Build Adjacency
        self.adj = np.zeros((self.num_qubits, self.num_qubits), dtype=bool)
        for k in self.pivots:
            r = self.pivots[k]
            for j in range(self.num_qubits):
                if j != k and self.matrix[r, j + self.num_qubits]:
                    self.adj[k, j] = 1
                    self.adj[j, k] = 1 
    
    def get_cz_count(self):
        return np.sum(np.triu(self.adj))

    def generate_circuit(self):
        circ = stim.Circuit()
        
        # 1. Prepare Graph State
        # If qubit is a pivot, it is X_k Z_N(k). We prep |+> and do CZ.
        # If qubit is NOT a pivot, what is it?
        # If it's 0 in matrix, it's disentangled.
        # If we just do H everywhere, we handle pivots correctly.
        # Non-pivots will be |+>.
        for k in range(self.num_qubits):
            circ.append("H", [k])
            
        rows, cols = np.where(np.triu(self.adj) == 1)
        for r, c in zip(rows, cols):
            circ.append("CZ", [r, c])
            
        # 2. Phase Correction
        # Calculate transformed stabilizers
        current_stabs = []
        for s in self.stabilizers:
            # Apply U to s
            # U is self.U
            t = self.U(s)
            current_stabs.append(t)
            
        # Check signs of pivots
        # For each pivot k, we expect X_k Z_neighbors.
        # We find the stabilizer corresponding to k.
        # It is at row self.pivots[k] in the matrix logic, but current_stabs might be permuted?
        # No, we permuted rows in self.matrix, but self.stabilizers list was not reordered in sync?
        # Ah! I permuted self.matrix rows but NOT self.stabilizers.
        # This is bad. The row operations in matrix correspond to multiplying stabilizers.
        # But I didn't track the multiplication on self.stabilizers.
        # So `current_stabs` (derived from original `self.stabilizers`) does NOT match `self.matrix`.
        # `current_stabs` are just the original stabilizers transformed by U.
        # But the basis of generators has changed by row operations!
        # I need to match the generators to the graph state generators.
        
        # Re-verify the generators from the circuit?
        # Or better: The graph state circuit generates a group.
        # I need to verify if my prepared state stabilizes the *original* group.
        # The phase correction needs to ensure that the prepared state has the correct signs
        # for the *transformed* group.
        
        # Actually, simpler approach:
        # I have the circuit: H + CZ + U_dag.
        # This prepares a state |psi>.
        # I check if |psi> stabilizes `self.stabilizers`.
        # If some stabilizers have -1, I can fix them?
        # No, if I have the wrong sign, I need to know *which* qubit Z to flip.
        # The diagonalization logic tells me that generator `r` (in matrix) corresponds to pivot `k`.
        # Generator `r` is a product of original stabilizers.
        # I didn't track which product.
        
        # Alternative:
        # Track the phase in `self.matrix`.
        # Add a column for sign? (0 or 1).
        # When multiplying rows, XOR the signs.
        # (S1 * S2) sign: sign(S1) * sign(S2) * i_factor.
        # i_factor depends on commutation.
        # This is getting complicated to implement manually.
        
        # Hacky fix:
        # Generate the circuit (H + CZ + U_dag).
        # Simulate it.
        # Check expectation of EACH pivot generator (from the matrix).
        # Wait, I don't have the pivot generators as PauliStrings because I didn't track row ops.
        
        # But I know the graph state structure!
        # The graph state has generators $g_k = X_k \prod Z_j$.
        # My circuit prepares these $g_k$ (with +1).
        # Then I apply $U^\dagger$.
        # So the state stabilizes $S'_k = U^\dagger g_k U$.
        # These $S'_k$ should span the same group as `self.stabilizers`.
        # The only issue is signs.
        # If the target group has a generator that corresponds to $-S'_k$, I'm off.
        
        # But `evaluate_optimization` (and `check_circuit`) checks the *original* stabilizers.
        # If I span the correct space, I satisfy the stabilizers up to signs.
        # If I am off by signs, I am in an orthogonal subspace.
        
        # Can I use `stim.Tableau.from_stabilizers`? 
        # It handles signs!
        # If I use `stim` to generate the initial tableau `T`.
        # Then I apply my Gaussian elimination to `T`?
        # `stim` doesn't expose the matrix directly for editing.
        # But I can query `T.x_output(k)`, `T.z_output(k)`.
        # These ARE the generators.
        # I can implement `diagonalize` using `T`.
        # - For k: find generator with X on k.
        #   (Scan T.z_output(r) for r in 0..N).
        #   If found, swap generators? (Not supported efficiently?)
        #   Wait, `T` is a map. The stabilizers are `T(Z_k)`.
        #   I can use `to_circuit(method="elimination")`? That's what baseline did.
        
        # Let's go back to: Why did `baseline` get 846?
        # Because it used generic elimination.
        # My `diagonalize` got 522 edges.
        # I just need to get the phases right.
        
        # Let's track the signs in `self.matrix`.
        # Add column `2*num_qubits`.
        # Initial signs: All +1 (0).
        # (Assuming inputs are + ...). Check input strings.
        # `stabilizers_task_v10.txt` has no signs?
        # "XXXX..." implies +1.
        # So initial signs are 0.
        
        # Row mult $R_j \leftarrow R_j * R_i$.
        # Sign update: $s_j \leftarrow s_j \oplus s_i \oplus phase(P_j, P_i)$.
        # $P_j, P_i$ are Pauli strings.
        # $P_j P_i = (-1)^p P_{new}$.
        # The phase arises if they anticommute?
        # No, they commute (stabilizers).
        # But product of two Paulis can have $i$ or $-1$.
        # $X \cdot Z = -i Y$. $Z \cdot X = i Y$.
        # $X \cdot X = I$. $Z \cdot Z = I$.
        # $Y \cdot Y = I$.
        # We need a `phase_product` function.
        # It depends on the number of non-commuting terms?
        # For commuting stabilizers, the product is always $\pm 1$ times a Pauli.
        # (No $i$).
        # Phase is $-1$ if ... ?
        # Standard formula: $s_{new} = s_1 + s_2 + g(P_1, P_2) \pmod 2$.
        # $g(x1,z1, x2,z2) = \sum (x1 z2 - x2 z1)$ ? No.
        # Stim can do this!
        # I can maintain a list of `stim.PauliString` mirroring the matrix.
        # When I swap rows, I swap the strings.
        # When I row_mult, I multiply the strings: `stabs[j] *= stabs[i]`.
        # This tracks the phase perfectly!
        
        # Then at the end, I have `stabs[k]` (the pivot row).
        # This stabilizer corresponds to the graph generator $g_k = X_k Z_{...}$.
        # `stabs[k]` should be exactly $\pm g_k$ (after applying `U`? No).
        # Wait.
        # I am doing row operations on the stabilizers $S$.
        # AND column operations (basis change) $U$.
        # Let $S_{current}$ be the list of stabilizers.
        # Column ops $U$ change the *basis* of the stabilizers?
        # No, if I apply $H_k$, I am changing the representation of the stabilizers in the NEW basis.
        # $S_{new} = H S_{old} H$.
        # So if I update `stabs[k]` by applying $H_k$ whenever I do `apply_H(k)`,
        # then `stabs[k]` always represents the stabilizers in the current frame.
        # At the end, `stabs[row]` should look like $\pm X_{pivot} Z_{adj}$.
        # If it is $-X...$, I have a -1 phase.
        # The graph state preparation makes $+X...$.
        # So I need a $Z$ correction on that pivot qubit.
        
        pass

    def diagonalize_with_signs(self):
        print("Diagonalizing with signs...")
        # Maintain stim PauliStrings
        self.current_stabs = [s.copy() for s in self.stabilizers]
        
        pivot_row = 0
        self.pivots = {} 
        
        for k in range(self.num_qubits):
            if pivot_row >= self.num_stab:
                break
                
            found = False
            for r in range(pivot_row, self.num_stab):
                # Check if X on k
                # Use the PauliString directly? Or the matrix?
                # Using matrix is faster for search.
                # Must keep matrix and stabs in sync.
                if self.matrix[r, k]:
                    if r != pivot_row:
                        self.matrix[[pivot_row, r]] = self.matrix[[r, pivot_row]]
                        self.current_stabs[pivot_row], self.current_stabs[r] = self.current_stabs[r], self.current_stabs[pivot_row]
                    found = True
                    break
            
            if not found:
                # Try H
                has_z = False
                for r in range(pivot_row, self.num_stab):
                    if self.matrix[r, k + self.num_qubits]:
                        has_z = True
                        break
                
                if has_z:
                    self.apply_H(k) 
                    # Apply H to all stabs at qubit k
                    # Create full tableau for H on k
                    T_H = stim.Tableau(self.num_qubits)
                    T_H.append(stim.Tableau.from_named_gate("H"), [k])
                    
                    for i in range(len(self.current_stabs)):
                        self.current_stabs[i] = T_H(self.current_stabs[i])
                        
                    # Re-search
                    for r in range(pivot_row, self.num_stab):
                        if self.matrix[r, k]:
                            if r != pivot_row:
                                self.matrix[[pivot_row, r]] = self.matrix[[r, pivot_row]]
                                self.current_stabs[pivot_row], self.current_stabs[r] = self.current_stabs[r], self.current_stabs[pivot_row]
                            found = True
                            break
            
            if found:
                pivot_stab = self.current_stabs[pivot_row]
                for r in range(self.num_stab):
                    if r != pivot_row and self.matrix[r, k]:
                        self.row_mult(pivot_row, r)
                        # Update stab
                        self.current_stabs[r] *= pivot_stab
                self.pivots[k] = pivot_row
                pivot_row += 1
        
        print(f"Num pivots: {len(self.pivots)}")
        non_pivots = [k for k in range(self.num_qubits) if k not in self.pivots]
        print(f"Non-pivots: {non_pivots}")
        
        # Fix Y -> X (S_dag)
        for k in self.pivots:
            r = self.pivots[k]
            if self.matrix[r, k + self.num_qubits]:
                self.apply_S_dag(k)
                # Update stabs
                T_S_dag = stim.Tableau(self.num_qubits)
                T_S_dag.append(stim.Tableau.from_named_gate("S_DAG"), [k])
                for i in range(len(self.current_stabs)):
                    self.current_stabs[i] = T_S_dag(self.current_stabs[i])
                    
        # Build Adjacency
        self.adj = np.zeros((self.num_qubits, self.num_qubits), dtype=bool)
        self.z_corrections = []
        
        for k in self.pivots:
            r = self.pivots[k]
            # Check phase
            # Expect + X_k ...
            # self.current_stabs[r] should be X_k * ...
            # Check sign
            if self.current_stabs[r].sign == -1:
                self.z_corrections.append(k)
            
            for j in range(self.num_qubits):
                if j != k and self.matrix[r, j + self.num_qubits]:
                    self.adj[k, j] = 1
                    self.adj[j, k] = 1

    def generate_circuit_corrected(self):
        circ = stim.Circuit()
        
        # Determine non-pivots
        pivots_set = set(self.pivots.keys())
        non_pivots = [k for k in range(self.num_qubits) if k not in pivots_set]
        
        # Apply H only to pivots
        for k in self.pivots:
            circ.append("H", [k])
            
        # CZs
        rows, cols = np.where(np.triu(self.adj) == 1)
        for r, c in zip(rows, cols):
            # If any qubit is non-pivot (and thus |0>), CZ is identity.
            # But strictly speaking we should include it or not?
            # If we include it, it does nothing on |0>.
            # If we exclude it, same.
            # But wait. If we apply X correction to non-pivot (to make |1>),
            # then CZ matters!
            # So we MUST include CZs involving non-pivots.
            circ.append("CZ", [r, c])
            
        # Z corrections for pivots (fix X signs)
        for k in self.z_corrections:
            circ.append("Z", [k])
            
        # X corrections for non-pivots (fix Z signs)
        # Check unused rows
        used_rows = set(self.pivots.values())
        unused_rows = [r for r in range(self.num_stab) if r not in used_rows]
        
        # We assume unused rows are Z-only on non-pivots.
        # If multiple rows constraint same non-pivot, we assume consistency.
        # We just need to satisfy them.
        for r in unused_rows:
            s = self.current_stabs[r]
            # Check which non-pivots have Z
            # (X should be 0)
            if s.sign == -1:
                # We need to flip a qubit.
                # Find the first non-pivot with Z in this row
                target = -1
                for k in non_pivots:
                    # Check Z on k
                    if self.matrix[r, k + self.num_qubits]:
                        target = k
                        break
                
                if target != -1:
                    circ.append("X", [target])
                    # We should technically flip sign of all rows sharing this qubit?
                    # But we apply X at the end (before U_dag).
                    # Actually, if we apply X to |0>, we get |1>.
                    # Ideally we do this before CZs?
                    # If we have edges between pivot and non-pivot.
                    # g_k = X_k Z_np.
                    # If np is |1>, Z_np = -1.
                    # So g_k becomes -1.
                    # So we need to flip sign of g_k (pivot correction).
                    # This interaction is tricky.
                    
                    # Better strategy:
                    # Apply X corrections to non-pivots FIRST (init to |1>).
                    # Then CZs.
                    # Then Z corrections to pivots.
                    pass
        
        # Wait, if I change initialization of non-pivot to |1>, 
        # I affect the signs of pivots connected to it!
        # This complicates things.
        # Can I handle this?
        # If I init non-pivot to |1>, then for every neighbor pivot P,
        # the generator X_P Z_np picks up a minus sign.
        # So I need to add Z to P?
        # Yes.
        # So:
        # 1. Init non-pivots (I or X).
        # 2. Init pivots (H).
        # 3. CZs.
        # 4. Check signs of pivots.
        #    The sign of pivot P is determined by:
        #    - Its own sign requirement (from self.z_corrections).
        #    - The state of its neighbors (if any are |1>).
        #    If neighbor is |1>, we get -1.
        #    If required is -1, and we get -1, we are good.
        #    If required is +1, and we get -1, we apply Z to P.
        
        # So I need to recalculate Z corrections for pivots based on X corrections for non-pivots.
        
        return circ


def run():
    opt = GraphStateOptimizer("stabilizers_task_v10.txt")
    opt.diagonalize_with_signs()
    
    print(f"Graph State CX: {opt.get_cz_count()}")
    
    final_circuit = opt.generate_circuit_corrected()
    
    print("Checking validity...")
    with open("stabilizers_task_v10.txt", "r") as f:
         stabs = [stim.PauliString(s.strip()) for s in f if s.strip()]
         
    if check_circuit(final_circuit, stabs):
        print("VALID")
        with open("candidate_graph.stim", "w") as f:
            f.write(str(final_circuit))
        # Also analyze metrics
        print(f"Circuit instructions: {len(final_circuit)}")
    else:
        print("INVALID - Preserves failed")
        sim = stim.TableauSimulator()
        sim.do(final_circuit)
        for i, s in enumerate(stabs):
            exp = sim.peek_observable_expectation(s)
            if exp != 1:
                print(f"Stab {i} failed with {exp}")
                if i > 5: break

if __name__ == "__main__":
    run()
