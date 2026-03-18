import stim
import numpy as np
import sys

def get_metrics(circuit):
    cx = 0
    vol = 0
    for op in circuit.flattened():
        if op.name == "CX" or op.name == "CNOT":
            # Count number of pairs
            cx += len(op.targets_copy()) // 2
        vol += len(op.targets_copy()) # Volume usually counts total gates (1-qubit + 2-qubit)
        # Wait, volume definition in prompt: "total gate count in the volume gate set (CX, CY, CZ, H, S, SQRT_X, etc.)"
        # If op is applied to N targets, does it count as 1 or N?
        # Standard volume counts operations * targets? 
        # Usually volume is depth * width, or number of gates.
        # Let's assume it means "total number of primitive gates".
        # A multi-target gate is multiple primitive gates.
        # So len(op.targets_copy()) / (1 if single qubit else 2 if two qubit)
        # But some ops are 1 qubit, some 2.
        # Simplify: just count targets for single qubit gates, targets/2 for 2 qubit gates.
        # Actually, let's just count total gate invocations.
    
    # Re-implementing volume to be safe and standard:
    real_vol = 0
    real_cx = 0
    for op in circuit.flattened():
        n = 0
        if op.name in ["CX", "CNOT", "CZ", "CY", "XC", "YC", "ZC", "SWAP", "ISWAP"]:
            n = 2
        else:
            n = 1
        
        count = len(op.targets_copy()) // n
        real_vol += count
        if op.name == "CX" or op.name == "CNOT":
            real_cx += count
            
    return real_cx, real_vol

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
                if p == 1 or p == 2: self.matrix[i, k] = 1 # X or Y has X component
                if p == 3 or p == 2: self.matrix[i, k + self.num_qubits] = 1 # Z or Y has Z component

    def apply_H(self, k):
        self.U.append(stim.Tableau.from_named_gate("H"), [k])
        # Update matrix: swap X and Z columns for qubit k
        # X -> Z, Z -> X. 
        # In symplectic form: x_new = z_old, z_new = x_old.
        self.matrix[:, [k, k+self.num_qubits]] = self.matrix[:, [k+self.num_qubits, k]]

    def apply_S(self, k):
        self.U.append(stim.Tableau.from_named_gate("S"), [k])
        # S: X -> Y = XZ, Z -> Z
        # x_new = x_old
        # z_new = z_old ^ x_old
        x_col = self.matrix[:, k].copy()
        z_col = self.matrix[:, k + self.num_qubits].copy()
        self.matrix[:, k + self.num_qubits] = z_col ^ x_col

    def apply_S_dag(self, k):
        self.U.append(stim.Tableau.from_named_gate("S_DAG"), [k])
        # S_dag: X -> -Y = -XZ? No.
        # S = diag(1, i). S X S^dag = Y. S Z S^dag = Z.
        # S^dag X S = -Y. S^dag Z S = Z.
        # Symplectic: X -> XZ, Z -> Z.
        # Same update for S and S_dag in symplectic matrix (ignoring phase signs for now).
        x_col = self.matrix[:, k].copy()
        z_col = self.matrix[:, k + self.num_qubits].copy()
        self.matrix[:, k + self.num_qubits] = z_col ^ x_col

    def row_mult(self, i, j):
        self.matrix[j, :] ^= self.matrix[i, :]

    def diagonalize_with_signs(self):
        # We process to get X-basis stabilizers with Z-type overlaps (graph state form)
        # Graph state stabilizers: S_i = X_i * Prod_{j in N(i)} Z_j
        # In matrix: X part is identity matrix. Z part is adjacency matrix.
        
        self.current_stabs = [s.copy() for s in self.stabilizers]
        pivot_row = 0
        self.pivots = {}
        
        for k in range(self.num_qubits):
            if pivot_row >= self.num_stab: break
            
            # Look for X component at k
            found = False
            for r in range(pivot_row, self.num_stab):
                if self.matrix[r, k]: # Has X_k
                    if r != pivot_row:
                        self.matrix[[pivot_row, r]] = self.matrix[[r, pivot_row]]
                        self.current_stabs[pivot_row], self.current_stabs[r] = self.current_stabs[r], self.current_stabs[pivot_row]
                    found = True
                    break
            
            if not found:
                # No X component. Check for Z component and Hadamard it to X.
                has_z = False
                for r in range(pivot_row, self.num_stab):
                    if self.matrix[r, k + self.num_qubits]: # Has Z_k
                        has_z = True
                        break
                if has_z:
                    self.apply_H(k) 
                    # Update current_stabs with H
                    T_H = stim.Tableau(self.num_qubits)
                    T_H.append(stim.Tableau.from_named_gate("H"), [k])
                    for i in range(len(self.current_stabs)):
                        self.current_stabs[i] = T_H(self.current_stabs[i])
                    
                    # Re-search for X component (which was Z)
                    for r in range(pivot_row, self.num_stab):
                        if self.matrix[r, k]:
                            if r != pivot_row:
                                self.matrix[[pivot_row, r]] = self.matrix[[r, pivot_row]]
                                self.current_stabs[pivot_row], self.current_stabs[r] = self.current_stabs[r], self.current_stabs[pivot_row]
                            found = True
                            break
            
            if found:
                # Eliminate X_k from other rows
                pivot_stab = self.current_stabs[pivot_row]
                for r in range(self.num_stab):
                    if r != pivot_row and self.matrix[r, k]:
                        self.row_mult(pivot_row, r)
                        self.current_stabs[r] *= pivot_stab
                self.pivots[k] = pivot_row
                pivot_row += 1
        
        # Now we have pivots. 
        # Ensure we have X_i Z... form. If we have Y_i, we need to fix it.
        # Y = XZ. In symplectic, X=1, Z=1.
        # If matrix[r, k] (X) is 1, and matrix[r, k+n] (Z) is 1, we have Y (or -Y).
        # We want pure X on the pivot.
        # Apply S_dag: X -> Y? No.
        # We want to remove Z component from pivot.
        # S_dag maps Y -> X. (S_dag Y S = X).
        # So if we have Y, applying S_dag converts it to X.
        
        T_S_dag = stim.Tableau(self.num_qubits)
        has_updates = False
        for k in self.pivots:
            r = self.pivots[k]
            if self.matrix[r, k + self.num_qubits]: # Has Z component (so X+Z = Y)
                self.apply_S_dag(k) 
                T_S_dag.append(stim.Tableau.from_named_gate("S_DAG"), [k])
                has_updates = True
        
        if has_updates:
             for i in range(len(self.current_stabs)):
                self.current_stabs[i] = T_S_dag(self.current_stabs[i])
                
        # Build Adjacency Matrix
        self.adj = np.zeros((self.num_qubits, self.num_qubits), dtype=bool)
        self.z_corrections = []
        for k in self.pivots:
            r = self.pivots[k]
            # Check sign
            if self.current_stabs[r].sign == -1:
                self.z_corrections.append(k)
            # Check Z neighbors
            for j in range(self.num_qubits):
                if j != k and self.matrix[r, j + self.num_qubits]:
                    self.adj[k, j] = 1
                    # self.adj[j, k] = 1 # Symmetry not guaranteed yet? 
                    # For a valid graph state, adj should be symmetric. 
                    # But stabilizers might be ordered arbitrarily.
                    # With full pivot elimination, X_k appears only in row r.
                    # Z_j can appear anywhere.
                    # The standard form is S_k = X_k * Prod Z_j.
                    # This implies symmetry is forced by commutativity?
                    # S_k S_j = S_j S_k.
                    # X_k Z_j ... vs X_j Z_k ...
                    # Commute if delta(k,j) ... wait.
                    # X_k Z_j commutes with X_j Z_k if (X_k Z_k) and (Z_j X_j) is -1 * -1 = 1.
                    # They commute.
                    # If we have X_k Z_j and X_j (no Z_k), they anti-commute.
                    # So Z_k must be present in S_j if Z_j is present in S_k?
                    pass

    def generate_circuit_corrected(self):
        circ = stim.Circuit()
        for k in range(self.num_qubits):
            circ.append("H", [k])
        
        # Use upper triangle to place CZs
        # Note: self.adj might not be perfectly symmetric if input stabilizers were weird, 
        # but for a stabilizer state it should imply a graph.
        # We rely on the fact that we can extract the graph from the Z components of the X-basis stabilizers.
        rows, cols = np.where(self.adj)
        # Filter to triu to avoid double counting and self-loops
        processed = set()
        
        cz_candidates = []
        for r, c in zip(rows, cols):
            if r < c:
                cz_candidates.append((r, c))
        
        for r, c in cz_candidates:
            circ.append("CZ", [r, c])
            
        for k in self.z_corrections:
            circ.append("Z", [k])
            
        # Transform back to target basis
        u_dag_circ = self.U.inverse().to_circuit()
        circ += u_dag_circ
        return circ

def run():
    print("Loading baseline...")
    with open("my_baseline.stim", "r") as f:
        baseline_text = f.read()
    print(f"Baseline text length: {len(baseline_text)}")
    try:
        baseline = stim.Circuit(baseline_text)
        base_cx, base_vol = get_metrics(baseline)
        print(f"Baseline CX: {base_cx}, Vol: {base_vol}")
    except Exception as e:
        print(f"Error loading baseline: {e}")
        base_cx = 99999
        base_vol = 99999

    print("Attempting Stim native synthesis...")
    with open("current_stabilizers.txt", "r") as f:
         stabs = [stim.PauliString(s.strip()) for s in f if s.strip()]
    
    try:
        tableau = stim.Tableau.from_stabilizers(stabs, allow_underconstrained=True)
        cand_stim = tableau.to_circuit(method="elimination")
        cand_cx, cand_vol = get_metrics(cand_stim)
        print(f"Stim Synthesis CX: {cand_cx}, Vol: {cand_vol}")
        
        if check_circuit(cand_stim, stabs):
             print("Stim Synthesis VALID")
             if cand_cx < base_cx:
                 print("Stim Synthesis is BETTER")
                 with open("candidate.stim", "w") as f:
                     f.write(str(cand_stim))
                 return # Success
             else:
                 print("Stim Synthesis is WORSE or EQUAL")
        else:
             print("Stim Synthesis INVALID")
    except Exception as e:
        print(f"Stim synthesis failed: {e}")

    print("Optimizing with Graph State...")
    opt = GraphStateOptimizer("current_stabilizers.txt")
    opt.diagonalize_with_signs()
    
    cand = opt.generate_circuit_corrected()
    cand_cx, cand_vol = get_metrics(cand)
    print(f"Candidate CX: {cand_cx}, Vol: {cand_vol}")
    
    # Check strict improvement
    if cand_cx < base_cx or (cand_cx == base_cx and cand_vol < base_vol):
        print("IMPROVEMENT FOUND")
    else:
        print("NO IMPROVEMENT")

    print("Checking validity...")
    with open("current_stabilizers.txt", "r") as f:
         stabs = [stim.PauliString(s.strip()) for s in f if s.strip()]
    
    if check_circuit(cand, stabs):
        print("VALID")
        with open("candidate.stim", "w") as f:
            f.write(str(cand))
    else:
        print("INVALID")
        sim = stim.TableauSimulator()
        sim.do(cand)
        failed_count = 0
        corrections = []
        for i, s in enumerate(stabs):
            exp = sim.peek_observable_expectation(s)
            if exp != 1:
                print(f"Stab {i} failed with {exp}")
                failed_count += 1
                if exp == -1:
                    # Try to fix by finding a Pauli that anticommutes with this stabilizer
                    # But we need to fix the STATE.
                    # If current state is -1 eigenstate, we need to flip it to +1.
                    # We need an operation P such that P |psi> is +1 eigenstate.
                    # S P |psi> = P S (-|psi>) = - P S |psi> ... wait.
                    # We want S (P |psi>) = +1 (P |psi>).
                    # P S P^dag = -S.
                    # If we find P that anticommutes with S, then P flips the eigenvalue.
                    # However, P might also flip other stabilizers!
                    # We need P that anticommutes with S_i and commutes with all other S_j (that are already +1).
                    # This is exactly the logical operators of the code.
                    # But we are in a stabilizer state (0 logical qubits).
                    # So there MUST exist such a P?
                    # No, if it's a unique stabilizer state, there are no logicals.
                    # But if we are in the wrong eigenstate (-1), it's a valid state orthogonal to the target.
                    # We just need to apply the destablizer?
                    # The set of stabilizers is maximal.
                    pass
        print(f"Failed {failed_count} stabilizers")

if __name__ == "__main__":
    run()
