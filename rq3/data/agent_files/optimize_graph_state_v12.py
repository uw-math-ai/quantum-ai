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
                if p == 1 or p == 2: self.matrix[i, k] = 1
                if p == 3 or p == 2: self.matrix[i, k + self.num_qubits] = 1

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

    def diagonalize_with_signs(self):
        print("Diagonalizing with signs...")
        self.current_stabs = [s.copy() for s in self.stabilizers]
        pivot_row = 0
        self.pivots = {}
        
        for k in range(self.num_qubits):
            if pivot_row >= self.num_stab: break
            found = False
            for r in range(pivot_row, self.num_stab):
                if self.matrix[r, k]:
                    if r != pivot_row:
                        self.matrix[[pivot_row, r]] = self.matrix[[r, pivot_row]]
                        self.current_stabs[pivot_row], self.current_stabs[r] = self.current_stabs[r], self.current_stabs[pivot_row]
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
                        self.current_stabs[r] *= pivot_stab
                self.pivots[k] = pivot_row
                pivot_row += 1
        
        # Fix Y -> X
        # Note: apply_S_dag logic requires matrix update, which we do.
        # But we also need to update current_stabs.
        # We can batch the tableau update.
        T_S_dag = stim.Tableau(self.num_qubits)
        has_updates = False
        for k in self.pivots:
            r = self.pivots[k]
            if self.matrix[r, k + self.num_qubits]:
                self.apply_S_dag(k) # Updates matrix and U
                T_S_dag.append(stim.Tableau.from_named_gate("S_DAG"), [k])
                has_updates = True
        
        if has_updates:
             for i in range(len(self.current_stabs)):
                self.current_stabs[i] = T_S_dag(self.current_stabs[i])
                
        self.adj = np.zeros((self.num_qubits, self.num_qubits), dtype=bool)
        self.z_corrections = []
        for k in self.pivots:
            r = self.pivots[k]
            if self.current_stabs[r].sign == -1:
                self.z_corrections.append(k)
            for j in range(self.num_qubits):
                if j != k and self.matrix[r, j + self.num_qubits]:
                    self.adj[k, j] = 1
                    self.adj[j, k] = 1

    def get_cz_count(self):
        return np.sum(np.triu(self.adj))

    def generate_circuit_corrected(self):
        circ = stim.Circuit()
        for k in range(self.num_qubits):
            circ.append("H", [k])
        rows, cols = np.where(np.triu(self.adj) == 1)
        for r, c in zip(rows, cols):
            circ.append("CZ", [r, c])
        for k in self.z_corrections:
            circ.append("Z", [k])
        u_dag_circ = self.U.inverse().to_circuit()
        circ += u_dag_circ
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
    else:
        print("INVALID - Preserves failed")
        sim = stim.TableauSimulator()
        sim.do(final_circuit)
        for i, s in enumerate(stabs):
            exp = sim.peek_observable_expectation(s)
            if exp != 1:
                print(f"Stab {i} failed with {exp}")
                if i > 40: break

if __name__ == "__main__":
    run()
