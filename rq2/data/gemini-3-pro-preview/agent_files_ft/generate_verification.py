import stim

# Read stabilizers
with open(r"C:\Users\anpaz\Repos\quantum-ai\rq2\data\gemini-3-pro-preview\agent_files_ft\stabilizers.txt", "r") as f:
    stabilizers = [l.strip() for l in f if l.strip()]

# Read baseline circuit
with open(r"C:\Users\anpaz\Repos\quantum-ai\rq2\data\gemini-3-pro-preview\agent_files_ft\baseline.stim", "r") as f:
    baseline_str = f.read()

circuit = stim.Circuit(baseline_str)
circuit.append("TICK")

# Add verification
# We use ancillas starting from 90
num_data = 90
ancilla_start = 90
flag_qubits = []

for i, s_str in enumerate(stabilizers):
    ancilla = ancilla_start + i
    flag_qubits.append(ancilla)
    
    # Init ancilla in |+> (R then H)
    circuit.append("R", [ancilla])
    circuit.append("H", [ancilla])
    
    # Apply controlled Paulis
    # Stabilizer string has 'X', 'Z', 'I'
    # s_str[j] is Pauli on qubit j
    targets = []
    for qubit_idx, p in enumerate(s_str):
        if p == 'X':
            circuit.append("CX", [ancilla, qubit_idx])
        elif p == 'Z':
            circuit.append("CZ", [ancilla, qubit_idx])
        elif p == 'Y':
            circuit.append("CY", [ancilla, qubit_idx]) # Stim supports CY
            
    # Measure ancilla in X basis (H then M)
    circuit.append("H", [ancilla])
    circuit.append("M", [ancilla])
    circuit.append("TICK")

# Write new circuit
with open(r"C:\Users\anpaz\Repos\quantum-ai\rq2\data\gemini-3-pro-preview\agent_files_ft\verification.stim", "w") as f:
    f.write(str(circuit))

print(f"Generated verification circuit with {len(stabilizers)} flags.")
print(f"Flag qubits: {flag_qubits[0]} to {flag_qubits[-1]}")
