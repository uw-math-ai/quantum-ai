import stim

def generate_solution():
    # Load original circuit
    with open("current.stim", "r") as f:
        original = f.read().strip()
    
    # Load stabilizers
    stabilizers = []
    with open("all_stabilizers.txt", "r") as f:
        for line in f:
            line = line.strip()
            if not line: continue
            if line.startswith('+'):
                line = line[1:]
            line = line.replace('_', 'I')
            stabilizers.append(line)
            
    # Stabilizer length
    stab_len = len(stabilizers[0])
    
    # Original circuit
    circuit = stim.Circuit(original)
    
    # We need to know where to start ancillas.
    # Stabilizers cover 0 to stab_len-1.
    # So first ancilla is stab_len.
    start_ancilla = stab_len
    
    # Append stabilizer measurements
    for i, s_str in enumerate(stabilizers):
        ancilla = start_ancilla + i
        
        # Identify X and Z targets
        x_targets = []
        z_targets = []
        for q, char in enumerate(s_str):
            if char == 'X':
                x_targets.append(q)
            elif char == 'Z':
                z_targets.append(q)
        
        # Build circuit
        if len(x_targets) > 0 and len(z_targets) == 0:
            # X-stabilizer: Measure in X basis.
            # Init |+> (H on |0>)
            circuit.append("H", [ancilla])
            
            # CNOTs (Ancilla control, Data target)
            for q in x_targets:
                circuit.append("CX", [ancilla, q])
                
            # Measure X (H then M)
            circuit.append("H", [ancilla])
            circuit.append("M", [ancilla])
            
        elif len(z_targets) > 0 and len(x_targets) == 0:
            # Z-stabilizer: Measure in Z basis.
            # Init |0>
            
            # CNOTs (Data control, Ancilla target)
            for q in z_targets:
                circuit.append("CX", [q, ancilla])
                
            # Measure Z
            circuit.append("M", [ancilla])
            
        else:
            # Mixed stabilizer
            # Measure in Z basis of Ancilla
            # Map X-targets to Z basis (H)
            
            # Apply H to X-targets
            if x_targets:
                circuit.append("H", x_targets)
                
            # CNOTs (Data control, Ancilla target)
            # Both X (now Z) and Z targets control the ancilla
            for q in x_targets + z_targets:
                circuit.append("CX", [q, ancilla])
                
            # Reverse H
            if x_targets:
                circuit.append("H", x_targets)
                
            circuit.append("M", [ancilla])
            
    print(circuit)

if __name__ == "__main__":
    generate_solution()
