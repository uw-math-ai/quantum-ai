import stim

def load_circuit(path):
    with open(path, 'r') as f:
        content = f.read()
    return stim.Circuit(content)

def load_chosen_stabilizers(path):
    stabs = []
    with open(path, 'r') as f:
        lines = f.readlines()
        for line in lines:
            line = line.strip()
            if not line: continue
            if ':' in line:
                idx, s = line.split(': ')
                stabs.append(s.strip())
            else:
                stabs.append(line)
    return stabs

def gen_ft_circuit(original_circuit, stabilizers):
    # Determine number of qubits
    num_qubits = 0
    # Scan circuit to find max qubit index
    for instr in original_circuit:
        if isinstance(instr, stim.CircuitRepeatBlock):
            pass # Assume no loops
        else:
            for t in instr.targets_copy():
                if t.is_qubit_target:
                    if t.value > num_qubits:
                        num_qubits = t.value
    num_qubits += 1
    
    # We will append gates to a new circuit
    ft_circuit = original_circuit.copy()
    
    current_qubit = num_qubits
    ancilla_indices = []
    
    for s_idx, s in enumerate(stabilizers):
        # Determine type and indices
        indices = [i for i, char in enumerate(s) if char != 'I']
        if not indices: continue
        
        type_char = s[indices[0]] 
        
        # Allocate ancillas
        measure_anc = current_qubit
        flag_anc = current_qubit + 1
        current_qubit += 2
        ancilla_indices.extend([measure_anc, flag_anc])
        
        # Add gadget
        if type_char == 'Z':
            # Z-stabilizer: check Parity of Z.
            # Ancilla (measure) init |0>.
            # Flag init |+>.
            # CX flag measure.
            # CX data measure.
            # CX flag measure.
            # Measure flag X. Measure measure Z.
            
            # 1. H flag
            ft_circuit.append("H", [flag_anc])
            
            # 2. CX flag measure
            ft_circuit.append("CX", [flag_anc, measure_anc])
            
            # 3. CX data measure (data control, measure target)
            for idx in indices:
                ft_circuit.append("CX", [idx, measure_anc])
                
            # 4. CX flag measure
            ft_circuit.append("CX", [flag_anc, measure_anc])
            
            # 5. H flag
            ft_circuit.append("H", [flag_anc])
            
            # Measurement
            ft_circuit.append("M", [measure_anc, flag_anc])
            
        elif type_char == 'X':
            # X-stabilizer.
            # Ancilla (measure) init |+>.
            # Flag init |+>.
            # CX measure flag.
            # CX measure data.
            # CX measure flag.
            # Measure flag X. Measure measure X.
            
            # 1. H measure
            ft_circuit.append("H", [measure_anc])
            
            # 2. H flag
            ft_circuit.append("H", [flag_anc])
            
            # 3. CX measure flag
            ft_circuit.append("CX", [measure_anc, flag_anc])
            
            # 4. CX measure data (measure control, data target)
            for idx in indices:
                ft_circuit.append("CX", [measure_anc, idx])
                
            # 5. CX measure flag
            ft_circuit.append("CX", [measure_anc, flag_anc])
            
            # 6. H measure, H flag
            ft_circuit.append("H", [measure_anc, flag_anc])
            
            # Measure
            ft_circuit.append("M", [measure_anc, flag_anc])
            
    return ft_circuit, ancilla_indices

if __name__ == "__main__":
    orig = load_circuit(r"C:\Users\anpaz\Repos\quantum-ai\rq2\data\gemini-3-pro-preview\agent_files_ft\input.stim")
    stabs = load_chosen_stabilizers(r"C:\Users\anpaz\Repos\quantum-ai\rq2\data\gemini-3-pro-preview\agent_files_ft\chosen_stabilizers.txt")
    
    print(f"Generating FT circuit for {len(stabs)} stabilizers...")
    ft_circ, ancillas = gen_ft_circuit(orig, stabs)
    
    # Save to candidate_ft_anpaz.stim
    with open(r"C:\Users\anpaz\Repos\quantum-ai\rq2\data\gemini-3-pro-preview\agent_files_ft\candidate_ft_anpaz.stim", "w") as f:
        f.write(str(ft_circ))
        
    print(f"Generated FT circuit with {len(ancillas)} ancillas.")
    
    # Write ancillas to file for return_result
    with open(r"C:\Users\anpaz\Repos\quantum-ai\rq2\data\gemini-3-pro-preview\agent_files_ft\ancillas_anpaz.txt", "w") as f:
        f.write(",".join(map(str, ancillas)))
