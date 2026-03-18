import stim
import numpy as np
import networkx as nx
import random
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
        
        # Working tableau (we will transform this)
        # We start with the stabilizers as the Z-output of a tableau?
        # Actually, let's just work with the PauliStrings and track the unitary U.
        # S_current = U * S_initial * U_dag
        # We want S_current to be graph state form.
        # Then |psi_target> = U_dag |Graph>
        
        # To track U, we use a stim.Tableau initialized to Identity
        self.U = stim.Tableau(self.num_qubits)
        
        # We need a mutable representation of stabilizers for Gaussian elim
        # Shape (num_stab, 2*num_qubits)
        # Columns 0..N-1 are X, N..2N-1 are Z
        self.matrix = np.zeros((self.num_stab, 2*self.num_qubits), dtype=bool)
        for i, s in enumerate(self.stabilizers):
            for k in range(self.num_qubits):
                p = s[k]
                if p == 1 or p == 2: # X or Y
                    self.matrix[i, k] = 1
                if p == 3 or p == 2: # Z or Y
                    self.matrix[i, k + self.num_qubits] = 1

    def apply_H(self, k):
        # Apply H to qubit k
        # Update U
        self.U.append(stim.Tableau.from_named_gate("H"), [k])
        # Update matrix: swap X and Z for col k
        self.matrix[:, [k, k+self.num_qubits]] = self.matrix[:, [k+self.num_qubits, k]]

    def apply_S(self, k):
        # Apply S to qubit k
        # Update U
        self.U.append(stim.Tableau.from_named_gate("S"), [k])
        # Update matrix
        x_col = self.matrix[:, k]
        z_col = self.matrix[:, k + self.num_qubits]
        self.matrix[:, k + self.num_qubits] = z_col ^ x_col

    def apply_S_dag(self, k):
        # Apply S_dag to qubit k
        self.U.append(stim.Tableau.from_named_gate("S_DAG"), [k])
        x_col = self.matrix[:, k]
        z_col = self.matrix[:, k + self.num_qubits]
        self.matrix[:, k + self.num_qubits] = z_col ^ x_col

    def row_mult(self, i, j):
        # Multiply row i into row j (S_j = S_j * S_i)
        self.matrix[j, :] ^= self.matrix[i, :]

    def diagonalize(self):
        print("Diagonalizing...")
        pivot_row = 0
        for k in range(self.num_qubits):
            if pivot_row >= self.num_stab:
                break
                
            # Find a row with X on k
            found = False
            for r in range(pivot_row, self.num_stab):
                if self.matrix[r, k]:
                    # Found X
                    if r != pivot_row:
                        # Swap rows
                        self.matrix[[pivot_row, r]] = self.matrix[[r, pivot_row]]
                    found = True
                    break
            
            if not found:
                # Try Hadamard to swap Z to X
                has_z = False
                for r in range(pivot_row, self.num_stab):
                    if self.matrix[r, k + self.num_qubits]:
                        has_z = True
                        break
                
                if has_z:
                    self.apply_H(k)
                    # Now search again
                    for r in range(pivot_row, self.num_stab):
                        if self.matrix[r, k]:
                            if r != pivot_row:
                                self.matrix[[pivot_row, r]] = self.matrix[[r, pivot_row]]
                            found = True
                            break
            
            if found:
                # Eliminate X on other rows
                for r in range(self.num_stab):
                    if r != pivot_row and self.matrix[r, k]:
                        self.row_mult(pivot_row, r)
                pivot_row += 1
            else:
                # No X or Z on this column in remaining rows? 
                # Qubit might be disentangled or dependent.
                pass

        # Now X part should be diagonal-ish. 
        # Check for Y's (X=1, Z=1) on the pivot diagonal.
        # We want X_i Z_... 
        # So we want X=1, Z=0 on the diagonal index.
        # But we might have permuted rows.
        # Let's map qubit k to row k?
        # We need to ensure that for each qubit k, there is a generator X_k Z_...
        # Our diagonalize ensures that for the pivot columns, we have X.
        # If num_stab < num_qubits, some qubits are not pivots.
        
        # Fix phases (remove Z from diagonal)
        # If X_k=1 and Z_k=1, we have Y_k. Apply S_dag to k: Y -> X.
        for r in range(self.num_stab):
            # Find the pivot column for this row
            pivot_col = -1
            for k in range(self.num_qubits):
                if self.matrix[r, k]:
                    pivot_col = k
                    break
            
            if pivot_col != -1:
                if self.matrix[r, pivot_col + self.num_qubits]:
                    # It's Y. Apply S_dag to convert to X
                    self.apply_S_dag(pivot_col)
                    # Now Z is 0 at pivot_col
        
        # Now we have graph state form for the subspace.
        # The adjacency matrix is the Z part of the matrix.
        # Note: The adjacency matrix A must be symmetric.
        # Extract A
        self.adj = np.zeros((self.num_qubits, self.num_qubits), dtype=bool)
        
        # Map pivots
        # For each row, the first X determines the qubit it "owns".
        self.qubit_to_row = {}
        for r in range(self.num_stab):
            for k in range(self.num_qubits):
                if self.matrix[r, k]:
                    self.qubit_to_row[k] = r
                    break
        
        # Build Adjacency
        for k in range(self.num_qubits):
            if k in self.qubit_to_row:
                r = self.qubit_to_row[k]
                # The neighbors are where Z is 1
                for j in range(self.num_qubits):
                    if j != k and self.matrix[r, j + self.num_qubits]:
                        self.adj[k, j] = 1
                        self.adj[j, k] = 1 # Enforce symmetry?
                        # Ideally it is already symmetric if it's a valid graph state.
                        # If not, the stabilizers might not be in perfect graph state form yet
                        # or we have free qubits.
    
    def get_cz_count(self):
        return np.sum(np.triu(self.adj))

    def optimize_graph(self, steps=2000):
        print("Optimizing graph...")
        G = nx.from_numpy_array(self.adj)
        current_edges = G.number_of_edges()
        print(f"Initial edges: {current_edges}")
        
        # We need to track basis changes during optimization
        # But wait, local complementation updates the graph AND implies a local Clifford.
        # We will reconstruct the circuit from the FINAL graph and the FINAL unitary.
        # Each LC step updates U.
        
        nodes = list(G.nodes())
        
        for step in range(steps):
            node = random.choice(nodes)
            
            # Try LC
            # Calculate delta edges
            neighbors = list(G.neighbors(node))
            if len(neighbors) < 2:
                continue
                
            subgraph_edges = 0
            for i in range(len(neighbors)):
                for j in range(i+1, len(neighbors)):
                    if G.has_edge(neighbors[i], neighbors[j]):
                        subgraph_edges += 1
            
            # New edges in subgraph = (n*(n-1)/2) - current_edges
            # Delta = new - old
            possible = (len(neighbors) * (len(neighbors) - 1)) // 2
            delta = possible - 2 * subgraph_edges
            
            if delta < 0:
                # Apply LC
                # Update Graph
                for i in range(len(neighbors)):
                    for j in range(i+1, len(neighbors)):
                        u, v = neighbors[i], neighbors[j]
                        if G.has_edge(u, v):
                            G.remove_edge(u, v)
                        else:
                            G.add_edge(u, v)
                
                # Update U
                # LC(a) = sqrt(-i X_a) prod sqrt(i Z_n)
                # U_new = LC(a) * U_old
                # We append LC(a) to U?
                # Actually, our circuit is: |psi> = U_dag |G>.
                # If |G> = LC(a)^dag |G'>, then |psi> = U_dag LC(a)^dag |G'> = (LC(a) U)^dag |G'>.
                # So we update U <- LC(a) U.
                
                # LC(a) op:
                # sqrt(-i X_a) = H S_dag H
                self.U.prepend(stim.Circuit(f"H {node}"), [node])
                self.U.prepend(stim.Circuit(f"S_DAG {node}"), [node])
                self.U.prepend(stim.Circuit(f"H {node}"), [node])
                
                for n in neighbors:
                    # sqrt(i Z_n) = S_n
                    self.U.prepend(stim.Circuit(f"S {n}"), [n])
                
                current_edges += delta
                if step % 100 == 0:
                    print(f"Step {step}: edges {current_edges}")

        self.adj = nx.to_numpy_array(G, nodelist=range(self.num_qubits))
        print(f"Final edges: {np.sum(np.triu(self.adj))}")

    def generate_circuit(self):
        circ = stim.Circuit()
        
        # 1. Prepare Graph State
        # H on all connected qubits? Or all qubits?
        # Graph state def: H on all vertices, then CZ.
        # Vertices are all qubits involved.
        for k in range(self.num_qubits):
            circ.append("H", [k])
            
        # CZs
        rows, cols = np.where(np.triu(self.adj) == 1)
        for r, c in zip(rows, cols):
            circ.append("CZ", [r, c])
            
        # 2. Apply U_dag
        # self.U is a tableau. We want the circuit implementing U^dag.
        # U.to_circuit() gives U.
        # U.inverse().to_circuit() gives U_dag.
        u_dag_circ = self.U.inverse().to_circuit()
        circ += u_dag_circ
        
        return circ

def run():
    opt = GraphStateOptimizer("stabilizers_task_v10.txt")
    opt.diagonalize()
    
    # Check initial cost
    print(f"Initial Graph State CX: {opt.get_cz_count()}")
    
    # Optimize
    opt.optimize_graph(steps=3000)
    
    # Generate
    final_circuit = opt.generate_circuit()
    
    # Clean up circuit (fuse gates)
    # Stim doesn't have a strong optimize method for 1-qubit gates exposed easily,
    # but we can just output it. The 1-qubit gates are secondary.
    # Primary is CX.
    
    # Check
    print("Checking validity...")
    with open("stabilizers_task_v10.txt", "r") as f:
         stabs = [stim.PauliString(s.strip()) for s in f if s.strip()]
         
    if check_circuit(final_circuit, stabs):
        print("VALID")
        # Write to file
        with open("candidate_graph.stim", "w") as f:
            f.write(str(final_circuit))
    else:
        print("INVALID - Preserves failed")

if __name__ == "__main__":
    run()
