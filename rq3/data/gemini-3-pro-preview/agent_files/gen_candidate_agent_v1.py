import stim

def generate_circuit():
    try:
        with open("target_stabilizers_prompt.txt", "r") as f:
            content = f.read().strip()
            # Split by comma
            stabs = [s.strip() for s in content.split(',')]
            # Remove empty strings if any
            stabs = [s for s in stabs if s]
            
        print(f"Read {len(stabs)} stabilizers.")
        if not stabs:
            print("No stabilizers found!")
            return

        lengths = [len(s) for s in stabs]
        print(f"Max length: {max(lengths)}")
        print(f"Min length: {min(lengths)}")
        
        paulis = [stim.PauliString(s) for s in stabs]
        
        tableau = stim.Tableau.from_stabilizers(paulis, allow_redundant=True, allow_underconstrained=True)
        print(f"Tableau qubits: {tableau.num_qubits}")
        
        circuit = tableau.to_circuit(method="graph_state")
        circ_str = str(circuit)
        
        new_lines = []
        rx_found = False
        for line in circ_str.splitlines():
            line = line.strip()
            if not line: continue
            
            if line.startswith("RX"):
                # RX 0 1 ... N
                # We replace with H 0 1 ... N
                parts = line.split()
                qubits = parts[1:]
                new_line = "H " + " ".join(qubits)
                new_lines.append(new_line)
                rx_found = True
            elif line.startswith("TICK"):
                continue
            else:
                new_lines.append(line)
                
        final_circuit = "\n".join(new_lines)
        
        if not rx_found:
            print("WARNING: No RX line found.")
            # If no RX, maybe it starts with something else?
            # Or maybe it's empty?
            
        with open("candidate.stim", "w") as f:
            f.write(final_circuit)
            
        print("Candidate written to candidate.stim")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    generate_circuit()
