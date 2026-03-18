import stim
import re

def main():
    with open("target_stabilizers_new.txt", "r") as f:
        content = f.read()
    
    stabilizers = [s.strip() for s in re.split(r'[,\n]+', content) if s.strip()]
    
    if not stabilizers:
        print("No stabilizers found.")
        return

    n_qubits = 85
    # print(f"Target qubits: {n_qubits}")
    
    fixed_stabilizers = []
    
    for i in range(0, len(stabilizers), 5):
        block = stabilizers[i:i+5]
        if not block:
            continue
            
        # Helper to strip I's
        def get_core(s):
            return s.lstrip('I').rstrip('I')
            
        core = get_core(block[0])
        
        # Calculate start offset from the FIRST element of the block
        first_offset = len(block[0]) - len(block[0].lstrip('I'))
        
        # Apply pattern to the block
        for j in range(len(block)):
            expected_offset = first_offset + j * 17
            
            # Reconstruct
            prefix = 'I' * expected_offset
            suffix_len = n_qubits - len(prefix) - len(core)
            
            if suffix_len < 0:
                # Should not happen if pattern is consistent
                # But if it does, it might mean the core wraps?
                # For this problem, it seems exact fit.
                suffix_len = 0
            
            new_s = 'I' * expected_offset + core + 'I' * suffix_len
            fixed_stabilizers.append(new_s)

    # Create Tableau
    try:
        tableau = stim.Tableau.from_stabilizers([stim.PauliString(s) for s in fixed_stabilizers])
    except Exception as e:
        print(f"Error creating tableau: {e}")
        return

    # Synthesize circuit
    circuit = tableau.to_circuit(method="graph_state")
    
    # Post-process to remove resets
    new_circuit = stim.Circuit()
    for instruction in circuit:
        if instruction.name == "RX":
            targets = instruction.targets_copy()
            new_circuit.append("H", targets)
        elif instruction.name == "R" or instruction.name == "RZ":
            pass
        elif instruction.name == "RY":
             targets = instruction.targets_copy()
             new_circuit.append("H", targets)
             new_circuit.append("S", targets)
        else:
            new_circuit.append(instruction)
            
    # Output to file
    with open("candidate_graph_new.stim", "w") as f:
        f.write(str(new_circuit))
    
    print("Candidate circuit generated: candidate_graph_new.stim")

if __name__ == "__main__":
    main()
