import stim

def analyze_circuit():
    with open(r'data/gemini-3-pro-preview/agent_files_ft/input_circuit.stim', 'r') as f:
        circuit_text = f.read()
    
    circuit = stim.Circuit(circuit_text)
    num_qubits = circuit.num_qubits
    print(f"Num qubits: {num_qubits}")
    
    used_qubits = set()
    for instruction in circuit:
        for target in instruction.targets_copy():
            if target.is_qubit_target:
                used_qubits.add(target.value)
    
    data_qubits = sorted(list(used_qubits))
    print(f"Data qubits: {data_qubits}")
    print(f"Max qubit index: {max(data_qubits)}")
    
    # Also read stabilizers to verify
    try:
        with open(r'data/gemini-3-pro-preview/agent_files_ft/stabilizers.txt', 'r') as f:
            stabs = f.read().strip().split('\n')
        print(f"Number of stabilizers: {len(stabs)}")
        print(f"Stabilizer length: {len(stabs[0])}")
    except FileNotFoundError:
        print("Stabilizers file not found yet")

if __name__ == "__main__":
    analyze_circuit()
