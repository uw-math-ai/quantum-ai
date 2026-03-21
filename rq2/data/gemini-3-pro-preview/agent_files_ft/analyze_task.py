import stim

try:
    with open("data/gemini-3-pro-preview/agent_files_ft/circuit.stim", "r") as f:
        circuit_str = f.read()
    
    with open("data/gemini-3-pro-preview/agent_files_ft/stabilizers.txt", "r") as f:
        stabilizers = [line.strip() for line in f.readlines() if line.strip()]

    print(f"Circuit length: {len(circuit_str)}")
    print(f"Number of stabilizers: {len(stabilizers)}")
    print(f"Stabilizer length: {len(stabilizers[0])}")
    
    # Parse circuit to find max qubit index
    c = stim.Circuit(circuit_str)
    print(f"Num qubits in circuit: {c.num_qubits}")
    
except Exception as e:
    print(f"Error: {e}")
