import stim

def generate_ft_circuit():
    circuit = stim.Circuit.from_file(r"C:\Users\anpaz\Repos\quantum-ai\rq2\data\gemini-3-pro-preview\agent_files_ft\circuit.stim")
    
    new_circuit = stim.Circuit()
    
    # Identify data qubits
    data_qubits = list(range(90))
    
    # We will build the circuit in passes
    # Pass 1: Copy initial RX and other non-CZ gates?
    # No, we should preserve order.
    
    current_ancilla = 90
    ancilla_list = []
    
    # Buffer for operations
    ops = []
    
    # Parse original circuit
    for instr in circuit:
        if instr.name == "CZ":
            targets = instr.targets_copy()
            for i in range(0, len(targets), 2):
                u = targets[i].value
                v = targets[i+1].value
                
                # Create gadget
                a = current_ancilla
                current_ancilla += 1
                ancilla_list.append(a)
                
                # We need to initialize 'a' in |+>
                # We can do it right here or at start.
                # Doing it here keeps locality.
                # RX a
                ops.append(stim.CircuitInstruction("RX", [a]))
                
                # CZ u a
                ops.append(stim.CircuitInstruction("CZ", [u, a]))
                
                # CZ v a
                ops.append(stim.CircuitInstruction("CZ", [v, a]))
                
                # H a
                ops.append(stim.CircuitInstruction("H", [a]))
                
                # M a
                ops.append(stim.CircuitInstruction("M", [a]))
                
                # Feedback: Z on u and v if M is 1
                # Stim uses rec[-1] for last measurement
                # CZ rec[-1] u
                # CZ takes targets list.
                t_rec = stim.target_rec(-1)
                new_circuit.append("CZ", [t_rec, u])
                new_circuit.append("CZ", [t_rec, v])
                
        else:
            new_circuit.append(instr)
            
    # Write to file
    with open(r"C:\Users\anpaz\Repos\quantum-ai\rq2\data\gemini-3-pro-preview\agent_files_ft\circuit_ft.stim", "w") as f:
        f.write(str(new_circuit))
        
    print(f"Generated FT circuit with {len(ancilla_list)} ancillas.")
    print(f"Flag qubits range: 90 to {current_ancilla-1}")
    
    # Save flag qubits list for tool call
    with open(r"C:\Users\anpaz\Repos\quantum-ai\rq2\data\gemini-3-pro-preview\agent_files_ft\flag_qubits.txt", "w") as f:
        f.write(",".join(map(str, ancilla_list)))

if __name__ == "__main__":
    generate_ft_circuit()
