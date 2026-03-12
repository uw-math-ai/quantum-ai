import stim
import sys

def generate_circuit():
    try:
        with open('current_target_stabilizers.txt', 'r') as f:
            lines = [l.strip() for l in f if l.strip()]
        
        # Convert to PauliStrings
        stabilizers = [stim.PauliString(l) for l in lines]
        
        # Create Tableau
        # allow_redundant=True is crucial as some stabilizers might be dependent
        # allow_underconstrained=True is crucial if the stabilizers don't fully specify the state (graph state method will pick one)
        tableau = stim.Tableau.from_stabilizers(stabilizers, allow_redundant=True, allow_underconstrained=True)
        
        # Synthesize circuit using graph state method
        # This uses H, S, CZ gates and produces a circuit with 0 CX gates
        circuit = tableau.to_circuit(method='graph_state')
        
        # Post-process circuit
        # 1. Remove R (Reset) gates - assuming input is |0>
        # 2. Replace RX (Reset X) with H - because RX |0> is |+>, and H |0> is |+>
        # 3. Replace RY (Reset Y) with H then S - because RY |0> is |i+>, and S H |0> is |i+>
        # 4. Remove M (Measurement) gates if any
        
        new_circuit = stim.Circuit()
        for instruction in circuit:
            if instruction.name == 'R':
                continue
            elif instruction.name == 'RX':
                # Replace RX with H on the same targets
                targets = instruction.targets_copy()
                new_circuit.append('H', targets)
            elif instruction.name == 'RY':
                # Replace RY with H then S on the same targets
                targets = instruction.targets_copy()
                new_circuit.append('H', targets)
                new_circuit.append('S', targets)
            elif instruction.name.startswith('M'):
                continue
            else:
                new_circuit.append(instruction)
                
        print(new_circuit)
        
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)

if __name__ == "__main__":
    generate_circuit()
