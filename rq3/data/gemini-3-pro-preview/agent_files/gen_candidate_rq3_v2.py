import stim

def get_stabilizers():
    with open("target_stabilizers_rq3_v2.txt", "r") as f:
        lines = [l.strip().strip(',') for l in f if l.strip()]
    stabs = []
    for l in lines:
        clean_l = l.strip()
        if clean_l.endswith(','):
            clean_l = clean_l[:-1]
        stabs.append(stim.PauliString(clean_l))
    return stabs

def generate_circuit():
    stabs = get_stabilizers()
    try:
        # Synthesize from stabilizers using graph state method
        tableau = stim.Tableau.from_stabilizers(stabs, allow_redundant=True, allow_underconstrained=True)
        circuit = tableau.to_circuit(method="graph_state")
        
        new_circuit = stim.Circuit()
        for instruction in circuit:
            if instruction.name == "RX":
                # Replace RX with H for standard initialization
                new_circuit.append("H", instruction.targets_copy())
            else:
                new_circuit.append(instruction)
        
        return new_circuit
    except Exception as e:
        print(f"Error creating from stabilizers: {e}")
        return None

if __name__ == "__main__":
    c = generate_circuit()
    if c:
        print(c)
