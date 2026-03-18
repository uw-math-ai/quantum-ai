import stim

def analyze_circuit():
    circuit = stim.Circuit.from_file("data/gemini-3-pro-preview/agent_files_ft/input_circuit.stim")
    print(f"Num qubits in circuit (by stim count): {circuit.num_qubits}")
    
    # Read stabilizers
    with open("data/gemini-3-pro-preview/agent_files_ft/stabilizers.txt", "r") as f:
        stabilizers = [line.strip() for line in f if line.strip()]
    
    print(f"Num stabilizers: {len(stabilizers)}")
    if stabilizers:
        print(f"Stabilizer length: {len(stabilizers[0])}")
    
    # Check max qubit index in circuit
    max_q = 0
    for instr in circuit:
        for target in instr.targets_copy():
            if target.is_qubit_target:
                max_q = max(max_q, target.value)
    print(f"Max qubit index in circuit used: {max_q}")

if __name__ == "__main__":
    analyze_circuit()
