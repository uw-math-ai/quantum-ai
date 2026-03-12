import stim

def generate():
    try:
        with open("target_stabilizers.txt", "r") as f:
            lines = [line.strip() for line in f if line.strip()]
        
        # Parse lines: +X__... -> +XII...
        stabs = []
        for line in lines:
            # remove '+' at start if present
            if line.startswith('+'):
                line = line[1:]
            # replace '_' with 'I'
            line = line.replace('_', 'I')
            stabs.append(stim.PauliString(line))
            
        print(f"Loaded {len(stabs)} stabilizers. Qubits: {len(stabs[0])}")
        
        # Synthesize
        tableau = stim.Tableau.from_stabilizers(stabs, allow_redundant=True, allow_underconstrained=True)
        circuit = tableau.to_circuit(method="graph_state")
        
        new_circuit = stim.Circuit()
        for instruction in circuit:
            if instruction.name in ["R", "RX", "RY", "RZ", "M", "MX", "MY", "MZ"]:
                 continue
            new_circuit.append(instruction)
            
        with open("candidate_from_file.stim", "w") as f:
            f.write(str(new_circuit))
        print("Candidate written to candidate_from_file.stim")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    generate()
