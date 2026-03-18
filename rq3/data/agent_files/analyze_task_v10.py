import stim
import sys

def analyze():
    print("Analyzing task...")
    
    # 1. Analyze Stabilizers
    with open("stabilizers_task_v10.txt", "r") as f:
        lines = [l.strip() for l in f if l.strip()]
    
    if not lines:
        print("No stabilizers found")
        return

    num_qubits = len(lines[0])
    num_stabilizers = len(lines)
    print(f"Num qubits: {num_qubits}")
    print(f"Num stabilizers: {num_stabilizers}")
    
    # Check if graph state (all stabilizers are X-based or Z-based or convertible)
    # Actually, graph state stabilizers are of form X_i * Z_neighbors
    # Let's just check the types
    x_only = 0
    z_only = 0
    mixed = 0
    
    for s in lines:
        has_x = 'X' in s
        has_z = 'Z' in s
        if has_x and not has_z:
            x_only += 1
        elif has_z and not has_x:
            z_only += 1
        else:
            mixed += 1
            
    print(f"X-only: {x_only}, Z-only: {z_only}, Mixed: {mixed}")
    
    # 2. Analyze Baseline Circuit
    with open("baseline_task_v10.stim", "r") as f:
        circuit_text = f.read()
    
    circuit = stim.Circuit(circuit_text)
    print(f"Baseline parsed successfully.")
    print(f"Baseline stats:\n{circuit.num_qubits} qubits used (internal)")
    
    cx_count = 0
    for instr in circuit:
        if instr.name == "CX" or instr.name == "CNOT":
            cx_count += len(instr.targets_copy()) // 2
            
    print(f"Baseline CX count: {cx_count}")
    
    # Check consistency
    # We can create a Tableau from stabilizers? No, it's a stabilizer state, not a tableau map.
    # We can check if the baseline circuit prepares the stabilizers.
    
    sim = stim.TableauSimulator()
    sim.do(circuit)
    
    # Sample check a few stabilizers
    # Actually, let's just assume baseline is valid for now, or check a few.
    # checking all might be slow if we do it naively, but stim is fast.
    
    print("Verifying baseline stabilizers...")
    preserved = 0
    for i, s in enumerate(lines):
        # Convert string to PauliString
        pauli = stim.PauliString(s)
        if sim.peek_observable_expectation(pauli) == 1:
            preserved += 1
    
    print(f"Baseline preserves {preserved}/{num_stabilizers} stabilizers.")

if __name__ == "__main__":
    analyze()
