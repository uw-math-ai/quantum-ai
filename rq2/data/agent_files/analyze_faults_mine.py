import stim
import sys

def load_file(path):
    with open(path, 'r') as f:
        return f.read().strip()

def analyze_faults():
    circuit_str = load_file("circuit.stim")
    circuit = stim.Circuit(circuit_str)
    
    stabs_str = load_file("stabilizers.txt").splitlines()
    stabilizers = []
    for s in stabs_str:
        if s.strip():
            stabilizers.append(stim.PauliString(s))
    
    # Check stabilizers
    print("Checking stabilizers...")
    sim = stim.TableauSimulator()
    sim.do(circuit)
    preserved = 0
    minus_one = 0
    zero = 0
    for i, s in enumerate(stabilizers):
        exp = sim.peek_observable_expectation(s)
        if exp == 1:
            preserved += 1
        elif exp == -1:
            minus_one += 1
        else:
            zero += 1
            if zero <= 5:
                print(f"Stabilizer {i} expectation: {exp}")

    print(f"Stabilizers preserved: {preserved}/{len(stabilizers)}")
    print(f"Stabilizers anti-preserved (-1): {minus_one}")
    print(f"Stabilizers undetermined (0): {zero}")
    
    # Backward propagation for fault analysis
    print("Analyzing faults...")
    num_qubits = 135
    threshold = 4
    
    l_x = [stim.PauliString(num_qubits) for _ in range(num_qubits)]
    l_z = [stim.PauliString(num_qubits) for _ in range(num_qubits)]
    for i in range(num_qubits):
        l_x[i][i] = 1 # X
        l_z[i][i] = 3 # Z
        
    ops = list(circuit.flattened())
    ops_reversed = ops[::-1]
    total_steps = len(ops)
    
    bad_faults = []
    
    for i, op in enumerate(ops_reversed):
        targets = []
        for t in op.targets_copy():
            if t.is_qubit_target:
                targets.append(t.value)
        
        name = op.name
        
        # Apply inverse gate (which is same for H, CX)
        if name == 'H':
            for q in targets:
                if q < num_qubits:
                    l_x[q], l_z[q] = l_z[q], l_x[q]
        elif name == 'CX':
            for k in range(0, len(targets), 2):
                c = targets[k]
                t = targets[k+1]
                if c < num_qubits and t < num_qubits:
                    # Backward propagation:
                    # X_c comes from X_c * X_t
                    # Z_t comes from Z_t * Z_c
                    l_x[c] *= l_x[t]
                    l_z[t] *= l_z[c]

        # Check faults *before* this gate (step total_steps - 1 - i)
        step_idx = total_steps - 1 - i
        
        check_set = set(targets)
        for q in check_set:
            if q >= num_qubits: continue
            
            # Check X
            w = sum(1 for k in range(num_qubits) if l_x[q][k]) 
            if w >= threshold:
                bad_faults.append([step_idx, q, 'X', w])
            
            # Check Z
            w = sum(1 for k in range(num_qubits) if l_z[q][k])
            if w >= threshold:
                bad_faults.append([step_idx, q, 'Z', w])

            # Check Y
            ly = l_x[q] * l_z[q]
            w = sum(1 for k in range(num_qubits) if ly[k])
            if w >= threshold:
                bad_faults.append([step_idx, q, 'Y', w])

    bad_faults.sort(key=lambda x: x[3], reverse=True)
    print(f"Found {len(bad_faults)} faults with weight >= {threshold}")
    print("Top 10 worst faults:")
    for bf in bad_faults[:10]:
        print(f"Step {bf[0]}: Qubit {bf[1]} {bf[2]} -> Weight {bf[3]}")

if __name__ == "__main__":
    analyze_faults()
