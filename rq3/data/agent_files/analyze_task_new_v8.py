import stim

def load_stabilizers(filename):
    with open(filename, 'r') as f:
        lines = f.readlines()
    stabilizers = [line.strip().replace('_', 'I') for line in lines if line.strip()]
    return stabilizers

def load_circuit(filename):
    with open(filename, 'r') as f:
        return stim.Circuit(f.read())

def check_stabilizers(circuit, stabilizers):
    sim = stim.TableauSimulator()
    sim.do(circuit)
    
    preserved = 0
    total = len(stabilizers)
    
    for stab in stabilizers:
        # Convert stabilizer string to PauliString
        pauli = stim.PauliString(stab)
        if sim.peek_observable_expectation(pauli) == 1:
            preserved += 1
    
    return preserved, total

def main():
    stabilizers = load_stabilizers('current_task_stabilizers.txt')
    baseline = load_circuit('current_task_baseline.stim')
    
    print(f"Loaded {len(stabilizers)} stabilizers.")
    print(f"Loaded baseline circuit with {len(baseline)} instructions.")
    
    preserved, total = check_stabilizers(baseline, stabilizers)
    print(f"Baseline preserves {preserved}/{total} stabilizers.")
    
    # Calculate metrics
    cx_count = sum(1 for op in baseline.flattened() if op.name == 'CX')
    volume = len(list(baseline.flattened()))
    print(f"Baseline metrics: CX={cx_count}, Volume={volume}")

if __name__ == "__main__":
    main()
