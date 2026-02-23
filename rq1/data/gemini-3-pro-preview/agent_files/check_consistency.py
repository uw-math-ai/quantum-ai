import stim
import numpy as np
import sys

def load_stabilizers(filename):
    with open(filename, 'r') as f:
        lines = [line.strip() for line in f if line.strip()]
    return lines

def symplectic_matrix(stabilizers):
    num_qubits = len(stabilizers[0])
    num_stabilizers = len(stabilizers)
    matrix = []
    
    for i, s_str in enumerate(stabilizers):
        # Clean the string first to remove non-Pauli characters (except +,-)?
        # stim handles +,-.
        # But if there are extra I's, stim will count them.
        
        # Check if line 95 is the issue.
        if len(s_str) != 119:
            # Maybe it has signs?
            # If s_str starts with + or -, check remaining length.
            pass
            
        p = stim.PauliString(s_str)
        if len(p) != num_qubits:
            print(f"Warning: Stabilizer {i} parsed length {len(p)} != {num_qubits}. Original: '{s_str}'")
            # Try to fix it? Truncate or pad?
            # If length is 121 and expected 119, maybe remove extra?
            if len(p) > num_qubits:
                # If trailing Is, maybe okay to truncate?
                # But need to be careful.
                # Let's assume the first 119 are correct if user said 119 qubits.
                pass
        
        row = []
        for k in range(len(p)):
            op = p[k]
            if op == 1: # X
                row.extend([1, 0])
            elif op == 2: # Y
                row.extend([1, 1])
            elif op == 3: # Z
                row.extend([0, 1])
            else: # I
                row.extend([0, 0])
        matrix.append(row)
        
    return np.array(matrix, dtype=int)

def check_consistency(stabilizers_file):
    stabilizers = load_stabilizers(stabilizers_file)
    # Clean stabilizers to ensure length 119
    # User said 119 qubits.
    # Detect if any stabilizer is length != 119.
    cleaned_stabilizers = []
    for i, s in enumerate(stabilizers):
        s_clean = s.strip()
        # Remove sign if present to check length of qubits part
        sign_char = ''
        if s_clean.startswith('+') or s_clean.startswith('-'):
            sign_char = s_clean[0]
            s_body = s_clean[1:]
        else:
            s_body = s_clean
            
        if len(s_body) > 119:
            print(f"Warning: Stabilizer {i} body length {len(s_body)} > 119. Truncating from START (heuristic based on check_pair.py).")
            # Heuristic: remove 2 chars from start for line 95 (or any length 121?)
            if len(s_body) == 121:
                s_body = s_body[2:]
            else:
                s_body = s_body[:119] # Fallback for other lengths

        elif len(s_body) < 119:
            print(f"Error: Stabilizer {i} body length {len(s_body)} < 119.")
            
        cleaned_stabilizers.append(sign_char + s_body)
    stabilizers = cleaned_stabilizers

    print(f'Loaded {len(stabilizers)} stabilizers.')
    
    ps = [stim.PauliString(s) for s in stabilizers]
    
    mat = symplectic_matrix(stabilizers)
    rows, cols = mat.shape
    num_qubits = cols // 2
    
    print(f'Matrix shape: {mat.shape}')
    
    reduced_mat = mat.copy()
    track = np.eye(rows, dtype=int)
    
    pivot_row = 0
    pivot_cols = []
    
    # Gaussian elimination
    for c in range(cols):
        if pivot_row >= rows:
            break
            
        pivot = -1
        for r in range(pivot_row, rows):
            if reduced_mat[r, c] == 1:
                pivot = r
                break
        
        if pivot == -1:
            continue
            
        if pivot != pivot_row:
            reduced_mat[[pivot_row, pivot]] = reduced_mat[[pivot, pivot_row]]
            track[[pivot_row, pivot]] = track[[pivot, pivot_row]]
            
        for r in range(rows):
            if r != pivot_row and reduced_mat[r, c] == 1:
                reduced_mat[r] = reduced_mat[r] ^ reduced_mat[pivot_row]
                track[r] = track[r] ^ track[pivot_row]
                
        pivot_cols.append(c)
        pivot_row += 1

    print(f'Rank: {pivot_row}')
    
    found_contradiction = False
    suspects = {32, 49, 82, 99, 112}
    
    for r in range(rows):
        if np.any(reduced_mat[r]):
             continue # Non-zero row
        
        # Zero row means dependency
        participating_indices = np.where(track[r])[0]
        if len(participating_indices) > 0:
            prod = stim.PauliString(num_qubits)
            for idx in participating_indices:
                prod = prod * ps[idx]
                
            if prod.weight == 0 and prod.sign == -1:
                print(f'\nCONTRADICTION FOUND!')
                print(f'Dependency among stabilizers {participating_indices} leads to -I.')
                intersect = set(participating_indices) & suspects
                print(f'Participating indices from suspect list: {sorted(list(intersect))}')
                found_contradiction = True
            elif prod.weight != 0:
                print(f'Error: Dependency calculation said row is zero but product is not identity? Weight: {prod.weight}')

    if not found_contradiction:
        print('\nNo contradictions found.')
        
        # Try to construct the tableau with stim to see if it complains or succeeds
        print("Attempting to construct tableau with stim...")
        try:
            tableau = stim.Tableau.from_stabilizers(ps, allow_underconstrained=True)
            print("Tableau construction SUCCESS.")
            
            # Check expectation values of all stabilizers
            print("Verifying stabilizers against generated tableau...")
            # To verify, we can look at the tableau's stabilizers or measure them.
            # But simpler: use tableau to measure observables.
            # Or convert to circuit and simulate?
            # tableau can directly compute expectation values?
            # No, but we can conjugate the stabilizers by the tableau inverse to see if they map to +Z.
            # If S maps to +Z_k or product of +Z's, it's stabilized.
            # If it maps to -Z... then it's -1.
            
            failures = []
            sim = stim.TableauSimulator()
            # Apply tableau to prepare the state
            # tableau is size num_qubits. Apply to qubits 0..num_qubits-1
            sim.do_tableau(tableau, list(range(num_qubits)))
            
            print("Simulator state prepared. Checking expectations...")
            
            for i, p in enumerate(ps):
                val = sim.peek_observable_expectation(p)
                if val != 1:
                    failures.append((i, val))
                    
            if failures:
                print(f"Tableau verification FAILED for {len(failures)} stabilizers.")
                print(f"First few failures: {failures[:10]}")
                
                # Check if the "known failures" are in the list
                suspects = {32, 49, 82, 99, 112}
                failed_indices = set(f[0] for f in failures)
                intersect = suspects & failed_indices
                if intersect:
                    print(f"Confirmed failures at suspect indices: {sorted(list(intersect))}")
                else:
                    print(f"Suspect indices {suspects} did NOT fail in this check.")
            else:
                print("Tableau verification SUCCESS: All stabilizers preserved (+1).")

        except Exception as e:
            print(f"Tableau construction FAILED: {e}")


if __name__ == '__main__':
    if len(sys.argv) > 1:
        check_consistency(sys.argv[1])
    else:
        check_consistency('data/gemini-3-pro-preview/agent_files/stabilizers_119.txt')

