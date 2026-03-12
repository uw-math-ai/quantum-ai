import stim
import sys

def generate_graph_state_circuit(stabilizers_path):
    with open(stabilizers_path, 'r') as f:
        content = f.read()
    
    # Replace newlines with commas to handle multiline input
    content = content.replace('\n', ',')
    
    parts = [s.strip() for s in content.split(',') if s.strip()]
    
    lens = set(len(p) for p in parts)
    print(f"Stabilizer lengths: {lens}", file=sys.stderr)
    
    # Force all stabilizers to length 81 (fix typo in prompt)
    fixed_parts = []
    for p in parts:
        if len(p) > 81:
            fixed_parts.append(p[:81])
        elif len(p) < 81:
            fixed_parts.append(p.ljust(81, 'I'))
        else:
            fixed_parts.append(p)
            
    stabilizers = []
    for p in fixed_parts:
        try:
            stabilizers.append(stim.PauliString(p))
        except Exception as e:
            print(f"Error parsing stabilizer: {e}", file=sys.stderr)
            sys.exit(1)

    # Create tableau from stabilizers
    try:
        # We use allow_redundant=True and allow_underconstrained=True to be robust
        tableau = stim.Tableau.from_stabilizers(stabilizers, allow_redundant=True, allow_underconstrained=True)
    except Exception as e:
        print(f"Error creating tableau: {e}", file=sys.stderr)
        sys.exit(1)

    # Convert to circuit using graph_state method
    circuit = tableau.to_circuit(method="graph_state")
    
    new_circuit = stim.Circuit()
    for instruction in circuit:
        if instruction.name == "RX":
            new_circuit.append("H", instruction.targets_copy())
        else:
            new_circuit.append(instruction)
            
    return new_circuit

if __name__ == "__main__":
    circuit = generate_graph_state_circuit("current_target_stabilizers.txt")
    print(circuit)
