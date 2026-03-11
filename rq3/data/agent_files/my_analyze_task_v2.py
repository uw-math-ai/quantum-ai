import stim

def analyze():
    # Load stabilizers
    with open('target_stabilizers_task_v2.txt', 'r') as f:
        lines = [line.strip().replace(',', '') for line in f if line.strip()]
    
    num_stabilizers = len(lines)
    num_qubits = len(lines[0])
    
    print(f"Number of stabilizers: {num_stabilizers}")
    print(f"Number of qubits: {num_qubits}")
    
    # Check consistency
    try:
        tableau = stim.Tableau.from_stabilizers([stim.PauliString(s) for s in lines], allow_underconstrained=True)
        print("Tableau successfully created from stabilizers.")
        print(f"Tableau len: {len(tableau)}")
    except Exception as e:
        print(f"Error creating tableau: {e}")

    # Analyze baseline
    try:
        circuit = stim.Circuit.from_file('my_task_baseline_v2.stim')
        print(f"Baseline circuit instructions: {len(circuit)}")
        print(f"Baseline num_qubits: {circuit.num_qubits}")
        
        # Count CX gates
        cx_count = 0
        for instruction in circuit:
            if instruction.name == "CX" or instruction.name == "CNOT":
                cx_count += len(instruction.targets_copy()) // 2
        print(f"Baseline CX count: {cx_count}")
        
    except Exception as e:
        print(f"Error analyzing baseline: {e}")

if __name__ == "__main__":
    analyze()
