import stim
import sys

def generate_circuit():
    try:
        with open('target_stabilizers_rq3.txt', 'r') as f:
            lines = [l.strip() for l in f if l.strip()]

        stabilizers = []
        for line in lines:
            try:
                stabilizers.append(stim.PauliString(line))
            except Exception as e:
                print(f"Error parsing stabilizer line: '{line}': {e}")
                continue

        print(f"Loaded {len(stabilizers)} stabilizers.")
        
        # Create tableau from stabilizers
        # allow_underconstrained=True because the list might not define a unique state
        # allow_redundant=True because stabilizers might be dependent
        tableau = stim.Tableau.from_stabilizers(stabilizers, allow_underconstrained=True, allow_redundant=True)
        
        # Synthesize circuit using graph_state method (produces H and CZ gates)
        circuit = tableau.to_circuit(method='graph_state')
        
        # Refine circuit: replace RX with H, remove R/M/MX
        new_circuit = stim.Circuit()
        for instruction in circuit:
            if instruction.name == 'RX':
                new_circuit.append("H", instruction.targets_copy())
            elif instruction.name in ['R', 'RZ', 'M', 'MX', 'MY', 'MZ']:
                pass
            else:
                new_circuit.append(instruction)

        # Output to candidate_rq3.stim
        with open('candidate_rq3.stim', 'w') as f:
            f.write(str(new_circuit).replace("tick", "")) 
        
        print("Candidate generated successfully.")
        
    except Exception as e:
        print(f"Error generating circuit: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    generate_circuit()
