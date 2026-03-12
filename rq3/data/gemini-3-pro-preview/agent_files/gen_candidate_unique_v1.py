import stim

def solve():
    with open('stabilizers.txt', 'r') as f:
        lines = [line.strip() for line in f if line.strip()]

    try:
        stabs = [stim.PauliString(s) for s in lines]
        tableau = stim.Tableau.from_stabilizers(stabs, allow_redundant=True, allow_underconstrained=True)
    except Exception as e:
        print(f"Error: {e}")
        return

    circuit = tableau.to_circuit(method="graph_state")
    
    new_circuit = stim.Circuit()
    for op in circuit:
        if op.name == 'R':
            continue 
        elif op.name == 'RX':
            new_circuit.append("H", op.targets_copy())
        elif op.name in ['M', 'MX', 'MY', 'MZ', 'MPP']:
            continue
        elif op.name == 'TICK':
            continue
        else:
            new_circuit.append(op)
            
    with open('candidate.stim', 'w') as f:
        print(new_circuit, file=f)
    print("Written to candidate.stim")

if __name__ == "__main__":
    solve()
