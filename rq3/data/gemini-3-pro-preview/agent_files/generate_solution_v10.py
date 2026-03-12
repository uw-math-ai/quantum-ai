import stim

def generate_graph_state_circuit():
    with open("target_stabilizers_v10.txt", "r") as f:
        lines = [l.strip() for l in f if l.strip()]
    
    stabilizers = []
    for line in lines:
        stabilizers.append(stim.PauliString(line))

    try:
        tableau = stim.Tableau.from_stabilizers(stabilizers, allow_underconstrained=True, allow_redundant=True)
    except Exception as e:
        print(f"Error creating tableau: {e}")
        return

    circuit = tableau.to_circuit(method="graph_state")
    
    new_circuit = stim.Circuit()
    for instruction in circuit:
        if instruction.name == "RX":
            new_circuit.append("H", instruction.targets_copy())
        else:
            new_circuit.append(instruction)
            
    # cx_count = new_circuit.num_gates("CX")
    # print(f"Generated circuit has {cx_count} CX gates.")
    
    with open("candidate_v10.stim", "w") as f:
        f.write(str(new_circuit))

if __name__ == "__main__":
    generate_graph_state_circuit()
