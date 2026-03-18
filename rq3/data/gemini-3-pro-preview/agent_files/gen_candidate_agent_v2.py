import stim
import sys

def generate_circuit():
    try:
        with open("target_stabilizers_prompt.txt", "r") as f:
            content = f.read().strip()
            stabs = [s.strip() for s in content.split(',') if s.strip()]
            
        print(f"Read {len(stabs)} stabilizers.")
        
        paulis = [stim.PauliString(s) for s in stabs]
        
        tableau = stim.Tableau.from_stabilizers(paulis, allow_redundant=True, allow_underconstrained=True)
        # print(f"Tableau qubits: {len(tableau)}") # Avoid potential attribute error
        
        circuit = tableau.to_circuit(method="graph_state")
        circ_str = str(circuit)
        
        new_lines = []
        rx_found = False
        
        for line in circ_str.splitlines():
            line = line.strip()
            if not line: continue
            
            if line.startswith("RX"):
                # Replace RX with H
                parts = line.split()
                # parts[0] is RX
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
            
        with open("candidate.stim", "w") as f:
            f.write(final_circuit)
            
        print("Candidate written to candidate.stim")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    generate_circuit()
