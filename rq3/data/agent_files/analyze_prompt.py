import stim
import sys

def analyze():
    # Load stabilizers
    with open('target_stabilizers_prompt.txt', 'r') as f:
        lines = [line.strip().replace(',', '') for line in f if line.strip()]
    
    stabilizers = []
    for line in lines:
        stabilizers.append(stim.PauliString(line))

    # Load baseline
    with open('baseline_prompt.stim', 'r') as f:
        circuit = stim.Circuit(f.read())
    
    num_qubits = len(lines[0])
    print(f"Number of qubits in stabilizers: {num_qubits}")
    print(f"Number of stabilizers: {len(stabilizers)}")
    print(f"Baseline circuit instruction count: {len(circuit)}")
    
    cx_count = circuit.num_2_qubit_gates()
    # Note: volume in the metric is total gate count in volume gate set.
    # We can approximate or just count all gates for now.
    
    print(f"Baseline CX count: {cx_count}")
    
    # Analyze stabilizer structure
    # Check if they are compatible with graph state synthesis
    # Graph states have generators K_i = X_i * Prod_{j in N(i)} Z_j
    # This means X is on diagonal (index i) and Zs are off-diagonal.
    # Let's see if we can transform the stabilizers into this form.

    # First, verify baseline works?
    sim = stim.TableauSimulator()
    sim.do(circuit)
    
    preserved = 0
    for stab in stabilizers:
        if sim.peek_observable_expectation(stab) == 1:
            preserved += 1
            
    print(f"Baseline preserved stabilizers: {preserved}/{len(stabilizers)}")

if __name__ == "__main__":
    analyze()
