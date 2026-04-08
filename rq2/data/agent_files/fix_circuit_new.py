import stim
import sys
import numpy as np
import os

try:
    import current_task_data
except ImportError:
    sys.path.append(os.getcwd())
    try:
        import current_task_data
    except ImportError:
        sys.exit("Could not import current_task_data")

STABILIZERS = current_task_data.stabilizers

def solve_linear_system(matrix, target):
    m, n = matrix.shape
    aug = np.hstack([matrix, target.reshape(-1, 1)])
    pivot_row = 0
    pivots = {}
    
    for col in range(n):
        if pivot_row >= m:
            break
        
        swap_row = -1
        for r in range(pivot_row, m):
            if aug[r, col] == 1:
                swap_row = r
                break
        
        if swap_row != -1:
            aug[[pivot_row, swap_row]] = aug[[swap_row, pivot_row]]
            pivots[pivot_row] = col
            for r in range(m):
                if r != pivot_row and aug[r, col] == 1:
                    aug[r] ^= aug[pivot_row]
            pivot_row += 1
            
    for r in range(m):
        # Check inconsistency: row is zero except last col
        if np.all(aug[r, :n] == 0) and aug[r, n] == 1:
            print("System inconsistent! Cannot fix with Paulis.")
            return

    solution = np.zeros(n, dtype=int)
    for r in range(m):
        if r in pivots:
            solution[pivots[r]] = aug[r, n]
            
    return solution

def fix_circuit(input_path, output_path, stabilizers):
    circuit = stim.Circuit.from_file(input_path)
    sim = stim.TableauSimulator()
    sim.do(circuit)
    
    num_qubits = 63 
    num_stabilizers = len(stabilizers)
    matrix = np.zeros((num_stabilizers, 2 * num_qubits), dtype=int)
    target = np.zeros(num_stabilizers, dtype=int)
    
    failed_count = 0
    
    for i, stab_str in enumerate(stabilizers):
        ps = stim.PauliString(stab_str)
        exp = sim.peek_observable_expectation(ps)
        if exp != 1:
            target[i] = 1
            failed_count += 1
            
    if failed_count == 0:
        print("Circuit is correct.")
        with open(output_path, "w") as f:
            f.write(str(circuit))
        return

    print(f"Failed count: {failed_count}")

    for i, stab_str in enumerate(stabilizers):
        ps = stim.PauliString(stab_str)
        for q in range(num_qubits):
            if q < len(ps):
                val = ps[q]
                x_s = 1 if val in [1, 2] else 0
                z_s = 1 if val in [3, 2] else 0
                matrix[i, 2*q] = z_s
                matrix[i, 2*q+1] = x_s
                
    solution = solve_linear_system(matrix, target)
    
    correction = stim.Circuit()
    for q in range(num_qubits):
        x_p = solution[2*q]
        z_p = solution[2*q+1]
        
        if x_p and z_p:
            correction.append("Y", [q])
        elif x_p:
            correction.append("X", [q])
        elif z_p:
            correction.append("Z", [q])
            
    final_circuit = circuit + correction
    
    with open(output_path, "w") as f:
        f.write(str(final_circuit))

if __name__ == "__main__":
    fix_circuit("candidate_initial.stim", "candidate_fixed.stim", STABILIZERS)
