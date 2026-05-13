
import stim

def generate_circuit():
    with open(r"data\gemini-3-pro-preview\agent_files_ft\circuit.stim", "r") as f:
        original_text = f.read().strip()
    with open(r"data\gemini-3-pro-preview\agent_files_ft\stabilizers.txt", "r") as f:
        stabs = f.read().splitlines()
        
    circuit = stim.Circuit(original_text)
    
    num_data = 161
    next_ancilla = 161
    ancilla_qubits = []
    flag_qubits_indices = []
    
    for s_str in stabs:
        weight = sum(1 for c in s_str if c in "XYZ")
        
        m = next_ancilla
        next_ancilla += 1
        ancilla_qubits.append(m)
        
        # Measurement gadget
        circuit.append("H", [m])
        
        targets = []
        for q, char in enumerate(s_str):
            if char == 'X':
                targets.append(("CX", q))
            elif char == 'Y':
                targets.append(("CY", q))
            elif char == 'Z':
                targets.append(("CZ", q))
        
        needs_flag = weight > 9
        flag = None
        if needs_flag:
            flag = next_ancilla
            next_ancilla += 1
            ancilla_qubits.append(flag)
            flag_qubits_indices.append(flag)
        
        # Determine split index
        # We need the number of interactions *after* the flag to be <= 9
        # Total interactions = weight.
        # We want count_after <= 9.
        # So count_before >= weight - 9.
        # We insert flag after `count_before` interactions.
        split_index = weight - 9
        if split_index < 0: split_index = 0
        
        count = 0
        for op_name, q in targets:
            if needs_flag and count == split_index:
                circuit.append("CX", [m, flag])
            
            circuit.append(op_name, [m, q])
            count += 1
            
        circuit.append("H", [m])
        circuit.append("M", [m])
        if needs_flag:
            circuit.append("M", [flag])
            
    return circuit, ancilla_qubits, flag_qubits_indices, stabs

if __name__ == "__main__":
    c, ancillas, flags, stabs = generate_circuit()
    with open(r"data\gemini-3-pro-preview\agent_files_ft\final_circuit.stim", "w") as f:
        f.write(str(c))
    print("Generated final_circuit.stim")
