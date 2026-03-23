import stim
import sys

def analyze_circuit(path):
    with open(path, 'r') as f:
        # read lines, strip whitespace
        circuit_str = f.read()
    
    circuit = stim.Circuit(circuit_str)
    
    # 45 data qubits
    num_qubits = 45 
    
    ops = []
    for op in circuit:
        ops.append(op)
    
    bad_faults = []
    
    # Iterate through all gates
    for i in range(len(ops)):
        op = ops[i]
        
        # Suffix circuit
        suffix_circuit = stim.Circuit()
        # Force size to 45 by adding Identity on qubit 44 (which is num_qubits-1)
        suffix_circuit.append("I", [num_qubits - 1])
        
        for j in range(i+1, len(ops)):
            suffix_circuit.append(ops[j])
            
        try:
            t = stim.Tableau.from_circuit(suffix_circuit)
        except Exception as e:
            # Maybe circuit is not Clifford? (e.g. measurements?)
            # The input has only Clifford gates.
            t = stim.Tableau(num_qubits)
        
        targets = op.targets_copy()
        qubits = [tg.value for tg in targets if tg.is_qubit_target]
        
        for q in qubits:
            for p_val in [1, 3]: # X=1, Z=3
                # Stim: 0=I, 1=X, 2=Y, 3=Z
                p_char = "IXYZ"[p_val]
                
                ps = stim.PauliString(num_qubits)
                ps[q] = p_val
                
                # Propagate forward using current tableau T
                try:
                    out_ps = t(ps)
                except Exception as e:
                    print(f"Error prop ps {ps} with t {t.num_qubits}: {e}")
                    continue
                
                # Weight
                w = 0
                for k in range(num_qubits):
                    if out_ps[k] != 0:
                        w += 1
                
                if w > 4:
                    bad_faults.append({
                        'op_idx': i,
                        'op': str(op),
                        'qubit': q,
                        'error': p_char,
                        'weight': w
                    })
    
    print(f"Total bad faults: {len(bad_faults)}")
    
    # Sort by op_idx then weight
    bad_faults.sort(key=lambda x: (x['op_idx'], -x['weight']))
    
    for f in bad_faults[:50]:
        print(f"Op {f['op_idx']} {f['op']}: Q{f['qubit']} {f['error']} -> W={f['weight']}")

if __name__ == "__main__":
    analyze_circuit("data/gemini-3-pro-preview/agent_files_ft/original.stim")
