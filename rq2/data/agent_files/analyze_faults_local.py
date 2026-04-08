import stim
import sys
import collections

def parse_stabilizers(filename):
    with open(filename, 'r') as f:
        lines = [line.strip() for line in f if line.strip()]
    return lines

def load_circuit(filename):
    with open(filename, 'r') as f:
        return stim.Circuit(f.read())

def analyze_faults(circuit_path, stabs_path):
    print(f"Loading circuit from {circuit_path}")
    circuit = load_circuit(circuit_path)
    stabilizers = parse_stabilizers(stabs_path)
    
    num_qubits = 105
    data_qubits = list(range(num_qubits))
    
    ops = list(circuit.flattened())
    max_q = 0
    for op in ops:
        for t in op.targets_copy():
            if t.is_qubit_target:
                max_q = max(max_q, t.value)
    
    num_qubits = max(num_qubits, max_q + 1)
    print(f"Num qubits: {num_qubits}")
    t = 4
    
    # 1. Check stabilizer preservation
    print("Checking stabilizer preservation...")
    sim = stim.TableauSimulator()
    sim.do(circuit)
    
    preserved = 0
    total_stabs = len(stabilizers)
    
    for s_str in stabilizers:
        pauli = stim.PauliString(s_str)
        exp = sim.peek_observable_expectation(pauli)
        if exp == 1:
            preserved += 1
            
    print(f"Stabilizers preserved: {preserved}/{total_stabs}")
    
    # 2. Fault propagation
    print("Analyzing faults...")
    
    ops = list(circuit.flattened())
    
    # Initialize future tableau as Identity
    # We use a large enough size.
    t_future = stim.Tableau(num_qubits + 10)
    
    bad_faults = []
    
    # Iterate backwards
    # We need to be careful with indexing.
    # ops[i] is the operation at index i.
    # Faults can occur after ops[i].
    
    # We will check faults *after* each op.
    # For the very last op, T_future is Identity.
    
    results = []
    worst_weight = 0
    bad_count = 0
    
    total_ops = len(ops)
    print(f"Total operations: {total_ops}")
    
    # We process in chunks to show progress? No need.
    
    for i in range(total_ops - 1, -1, -1):
        op = ops[i]
        
        # Determine targets for fault injection
        targets = []
        for t_ptr in op.targets_copy():
            if t_ptr.is_qubit_target:
                targets.append(t_ptr.value)
        
        # Inject faults on targets
        for q in targets:
            if q >= num_qubits: continue # Skip ancillas not in data set if any
            
            for p_char in ['X', 'Y', 'Z']:
                # Construct Pauli
                p = stim.PauliString(num_qubits + 10)
                if p_char == 'X': p[q] = 1
                elif p_char == 'Y': p[q] = 2
                elif p_char == 'Z': p[q] = 3
                
                # Propagate
                propagated = t_future(p)
                
                # Check weight on data qubits
                w = 0
                # Using a loop is slow in python?
                # Propagated is a PauliString.
                # We can convert to numpy? No, PauliString slice.
                # Or just iterate.
                # Optimization: check weight only if relevant?
                # But we need exact weight.
                
                # `weight` method gives total weight.
                # If all qubits are data qubits, then `propagated.weight` is enough.
                # Assuming 0-104 are data qubits.
                # If size > 105, we might have ancillas.
                # But currently no ancillas.
                
                w = sum(1 for k in data_qubits if propagated[k])
                
                if w >= t:
                    bad_count += 1
                    if w > worst_weight:
                        worst_weight = w
                    
                    results.append({
                        'op_index': i,
                        'gate': str(op),
                        'qubit': q,
                        'pauli': p_char,
                        'weight': w
                    })

        # Update T_future
        # T_new = T_Gk.then(T_future)
        # Create T_Gk
        # We use from_circuit for op
        op_c = stim.Circuit()
        op_c.append("I", [len(t_future)-1]) # Force size
        op_c.append(op)
        op_tableau = stim.Tableau.from_circuit(op_c)
        
        t_future = op_tableau.then(t_future)
        
    print(f"Bad faults found: {bad_count}")
    print(f"Max weight: {worst_weight}")
    
    results.sort(key=lambda x: x['weight'], reverse=True)
    print("Top 5 worst faults:")
    for res in results[:5]:
        print(res)

if __name__ == "__main__":
    analyze_faults("C:/Users/anpaz/Repos/quantum-ai/rq2/circuit_input.stim", "C:/Users/anpaz/Repos/quantum-ai/rq2/stabilizers_input.txt")
