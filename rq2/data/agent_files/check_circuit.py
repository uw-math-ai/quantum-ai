import stim
import sys

def get_rank(rows, num_cols):
    if not rows: return 0
    m = [list(r) for r in rows]
    pivot_row = 0
    num_rows = len(m)
    for col in range(num_cols):
        if pivot_row >= num_rows: break
        swap_idx = -1
        for r in range(pivot_row, num_rows):
            if m[r][col]:
                swap_idx = r
                break
        if swap_idx == -1: continue
        m[pivot_row], m[swap_idx] = m[swap_idx], m[pivot_row]
        for r in range(pivot_row + 1, num_rows):
            if m[r][col]:
                for c in range(col, num_cols):
                    m[r][c] ^= m[pivot_row][c]
        pivot_row += 1
    return pivot_row

def analyze_and_extract(circuit_path, stabs_path):
    with open(circuit_path, 'r') as f:
        circuit_str = f.read()
    circuit = stim.Circuit(circuit_str)
    ops = list(circuit)
    num_qubits = 45
    
    with open(stabs_path, 'r') as f:
        stab_lines = [l.strip() for l in f if l.strip()]
    stabs = []
    for l in stab_lines:
        try: stabs.append(stim.PauliString(l.replace(',', '').replace(' ', '')))
        except: pass
    
    stab_rows = []
    for s in stabs:
        row = []
        for k in range(num_qubits):
            row.append(1 if s[k] in [1, 2] else 0)
        for k in range(num_qubits):
            row.append(1 if s[k] in [2, 3] else 0)
        stab_rows.append(row)
        
    num_cols = 2 * num_qubits
    base_rank = get_rank(stab_rows, num_cols)
    
    extra_measurements = []
    
    for i in range(len(ops)):
        op = ops[i]
        
        suffix_circuit = stim.Circuit()
        suffix_circuit.append("I", [num_qubits - 1])
        for j in range(i+1, len(ops)):
            suffix_circuit.append(ops[j])
        
        try: t = stim.Tableau.from_circuit(suffix_circuit)
        except: t = stim.Tableau(num_qubits)
            
        targets = op.targets_copy()
        qubits = [tg.value for tg in targets if tg.is_qubit_target]
        
        for q in qubits:
            for p_val in [1, 3]: 
                ps = stim.PauliString(num_qubits)
                ps[q] = p_val
                try: out_ps = t(ps)
                except: continue
                
                w = out_ps.weight
                if w > 4:
                    caught = False
                    for s in stabs:
                        if not out_ps.commutes(s):
                            caught = True
                            break
                    
                    if not caught:
                        row = []
                        for k in range(num_qubits):
                            val = out_ps[k]
                            row.append(1 if val in [1, 2] else 0)
                        for k in range(num_qubits):
                            val = out_ps[k]
                            row.append(1 if val in [2, 3] else 0)
                        
                        new_rank = get_rank(stab_rows + [row], num_cols)
                        if new_rank > base_rank:
                            extra_measurements.append(str(out_ps))
    
    unique_extras = sorted(list(set(extra_measurements)))
    print(f"Extra logical operators to measure: {len(unique_extras)}")
    for e in unique_extras:
        print(f"LOGICAL: {e}")

if __name__ == "__main__":
    analyze_and_extract("data/gemini-3-pro-preview/agent_files_ft/original.stim", 
                        "data/gemini-3-pro-preview/agent_files_ft/stabilizers_correct.txt")
