import stim

def inspect_raw():
    lines = []
    with open("current_stabilizers.txt", "r") as f:
        for l in f:
            l = l.strip().replace(",", "")
            if l:
                lines.append(stim.PauliString(l))
    
    tableau = stim.Tableau.from_stabilizers(lines, allow_underconstrained=True)
    circuit = tableau.to_circuit(method="graph_state")
    
    print("Raw circuit first 20 lines:")
    for i, inst in enumerate(circuit):
        if i < 20:
            print(inst)

if __name__ == "__main__":
    inspect_raw()
