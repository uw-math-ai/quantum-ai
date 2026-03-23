import stim
import sys

# Define function
def generate_ft_circuit(circuit_path, stabs_path, output_path):
    with open(circuit_path, 'r') as f:
        circuit_text = f.read()
    
    stabs_lines = []
    with open(stabs_path, 'r') as f:
        for line in f:
            if line.strip(): stabs_lines.append(line.strip())
        
    circuit = stim.Circuit(circuit_text)
    
    max_idx = -1
    for op in circuit.flattened_operations():
        for t in op.targets:
            if t.value > max_idx:
                max_idx = t.value
    
    if max_idx < 74: max_idx = 74
    
    current_ancilla = max_idx + 1
    ancilla_list = []
    
    # We append to the circuit object
    print(f"Starting to process {len(stabs_lines)} stabilizers...")
    
    for i, stab_str in enumerate(stabs_lines):
        if i % 10 == 0: print(f"Processing stabilizer {i}")
        m = current_ancilla
        f = current_ancilla + 1
        current_ancilla += 2
        
        ancilla_list.append(m)
        ancilla_list.append(f)
        
        # Gadget:
        # H m, H f
        circuit.append("H", [m, f])
        
        # CZ m f
        circuit.append("CZ", [m, f])
        
        # Stabilizer check (controlled by m)
        # We need to construct the sequence of controlled Paulis
        # Note: Order matters for non-commuting Paulis? No, they commute within stabilizer.
        # But order of CX/CZ might affect error propagation.
        # We use standard order (0 to 74).
        
        for q_idx, p in enumerate(stab_str):
            if p == 'I': continue
            if p == 'X':
                circuit.append("CX", [m, q_idx])
            elif p == 'Z':
                circuit.append("CZ", [m, q_idx])
            elif p == 'Y':
                circuit.append("CY", [m, q_idx])
        
        # CZ m f
        circuit.append("CZ", [m, f])
        
        # H m, H f
        circuit.append("H", [m, f])
        
    # Measure ancillas at the end
    circuit.append("M", ancilla_list)
    
    # Save circuit
    with open(output_path, 'w') as f:
        f.write(str(circuit))
        
    print(f"Generated circuit with {current_ancilla} qubits.")
    
    # Save ancilla list to file for reading
    with open(output_path + ".ancillas", 'w') as f:
        f.write(",".join(map(str, ancilla_list)))

generate_ft_circuit(
    r"C:\Users\anpaz\Repos\quantum-ai\rq2\data\gemini-3-pro-preview\agent_files_ft\current.stim",
    r"C:\Users\anpaz\Repos\quantum-ai\rq2\data\gemini-3-pro-preview\agent_files_ft\current_stabs.txt",
    r"C:\Users\anpaz\Repos\quantum-ai\rq2\data\gemini-3-pro-preview\agent_files_ft\candidate.stim"
)
