import stim

def generate_circuit():
    try:
        with open('target_stabilizers.txt', 'r') as f:
            lines = [line.strip() for line in f if line.strip()]
        
        print(f"Loaded {len(lines)} stabilizers.")
        
        stabilizers = []
        for line in lines:
            try:
                stabilizers.append(stim.PauliString(line))
            except:
                print(f"Failed to parse line: {line}")
                return
            
        # Use allow_redundant=True and allow_underconstrained=True
        # because the stabilizers might be redundant or incomplete
        tableau = stim.Tableau.from_stabilizers(stabilizers, allow_redundant=True, allow_underconstrained=True)
        circuit = tableau.to_circuit(method="graph_state")
        
        with open('candidate_graph_v2.stim', 'w') as f:
            f.write(str(circuit))
            
        print("Candidate circuit generated successfully.")
        print(f"Circuit gates: {len(circuit)}")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    generate_circuit()
