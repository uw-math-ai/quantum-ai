import stim

def generate_ft_circuit():
    circuit = stim.Circuit.from_file(r"C:\Users\anpaz\Repos\quantum-ai\rq2\data\gemini-3-pro-preview\agent_files_ft\circuit.stim")
    
    new_circuit = stim.Circuit()
    
    current_ancilla = 90
    ancilla_list = []
    
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
                
                # Init a in |+>
                # RX a
                new_circuit.append("RX", [a])
                
                # CZ u a
                new_circuit.append("CZ", [u, a])
                
                # CZ v a
                new_circuit.append("CZ", [v, a])
                
                # H a (to measure in X)
                new_circuit.append("H", [a])
                
                # M a (measure in Z basis, effectively X basis)
                new_circuit.append("M", [a])
                
                # Feedback: Z on u and v if M is 1
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
