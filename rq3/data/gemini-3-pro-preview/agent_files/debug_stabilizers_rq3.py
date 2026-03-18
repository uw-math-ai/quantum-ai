import stim

try:
    with open("target_stabilizers_rq3.txt", "r") as f:
        lines = [line.strip() for line in f if line.strip()]

    print(f"Number of lines: {len(lines)}")
    lengths = [len(l) for l in lines]
    print(f"Max length: {max(lengths)}")
    print(f"Min length: {min(lengths)}")

    ps = [stim.PauliString(line) for line in lines]
    
    # Check if any pauli string is length != 49
    for p in ps:
        if len(p) != 49:
            print(f"PauliString length {len(p)} != 49")
            
    t = stim.Tableau.from_stabilizers(ps, allow_redundant=True, allow_underconstrained=True)
    print(f"Tableau num_qubits: {t.num_qubits}")

    c = t.to_circuit(method="graph_state")
    print(f"Circuit num_qubits: {c.num_qubits}")
    
except Exception as e:
    print(f"Error: {e}")
