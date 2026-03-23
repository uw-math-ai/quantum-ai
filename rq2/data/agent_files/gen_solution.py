import stim

def generate_solution():
    # Load original circuit
    circuit_file = r'C:\Users\anpaz\Repos\quantum-ai\rq2\data\gemini-3-pro-preview\agent_files_ft\input_circuit.stim'
    with open(circuit_file, 'r') as f:
        original = stim.Circuit(f.read())
        
    # Load stabilizers
    stabs_file = r'C:\Users\anpaz\Repos\quantum-ai\rq2\data\gemini-3-pro-preview\agent_files_ft\stabilizers_rq2.txt'
    stabilizers = []
    with open(stabs_file, 'r') as f:
        for line in f:
            if line.strip():
                stabilizers.append(stim.PauliString(line.strip()))
                
    # Load chosen indices
    chosen_file = r'C:\Users\anpaz\Repos\quantum-ai\rq2\data\gemini-3-pro-preview\agent_files_ft\chosen_stabilizers.txt'
    chosen_indices = []
    with open(chosen_file, 'r') as f:
        for line in f:
            if line.strip():
                chosen_indices.append(int(line.strip()))
                
    # Build new circuit
    new_circuit = stim.Circuit()
    new_circuit += original
    
    # Add measurements
    # We need ancillas. Start from qubit 63.
    num_data_qubits = 63
    ancilla_start = num_data_qubits
    
    # We will initialize all ancillas at once?
    # Or one by one?
    # "All ancilla qubits must be initialized in the |0> state and measured at the end of the circuit."
    # We can just use them. Implicitly 0 if new?
    # No, usually we should reset them or assume 0.
    # The prompt says "All ancilla qubits must be initialized in the |0> state".
    # Since we are outputting a full circuit, we can rely on default |0> initialization at start?
    # But the prompt input circuit doesn't have R 0 ...
    # It starts with gates.
    # If I introduce new qubits, they are |0>.
    # But I should probably add `R` or assume |0>.
    # Stim assumes |0>.
    
    ancilla_map = {} # stab_idx -> ancilla_idx
    
    # Apply H to all ancillas
    current_ancilla = ancilla_start
    ancillas = []
    for idx in chosen_indices:
        ancilla_map[idx] = current_ancilla
        ancillas.append(current_ancilla)
        current_ancilla += 1
        
    new_circuit.append('H', ancillas)
    
    # Apply controlled-Pauli gates
    # We can group them to minimize depth, but "Do not reorder gates" applies to original.
    # For new part, we can do whatever.
    # But parallel ops are better.
    # We iterate through chosen stabilizers.
    
    for idx in chosen_indices:
        stab = stabilizers[idx]
        ancilla = ancilla_map[idx]
        
        # stab is PauliString.
        # Length 63.
        # We iterate over the PauliString
        for q_idx in range(len(stab)):
            p = stab[q_idx] # returns int: 0=I, 1=X, 2=Y, 3=Z
            if p == 0: continue
            
            gate = None
            if p == 1: gate = 'CX' # C-X
            elif p == 2: gate = 'CY' # C-Y
            elif p == 3: gate = 'CZ' # C-Z
            
            new_circuit.append(gate, [ancilla, q_idx])
            
    # Apply H to all ancillas
    new_circuit.append('H', ancillas)
    
    # Measure ancillas
    new_circuit.append('M', ancillas)
    
    # Return result
    # We need to output "ancilla_qubits" list too.
    return new_circuit, ancillas

if __name__ == '__main__':
    c, ancillas = generate_solution()
    
    # Write to file
    out_file = r'C:\Users\anpaz\Repos\quantum-ai\rq2\data\gemini-3-pro-preview\agent_files_ft\candidate_ft.stim'
    with open(out_file, 'w') as f:
        f.write(str(c))
        
    print(f"Generated solution with {len(ancillas)} ancillas.")
    print(f"Circuit written to {out_file}")
    
    # Also print ancillas list for the return_result tool
    print("Ancillas:", ancillas)
