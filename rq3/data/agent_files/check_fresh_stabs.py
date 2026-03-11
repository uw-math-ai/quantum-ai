import stim

def check():
    with open('target_stabilizers_fresh.txt', 'r') as f:
        lines = [l.strip() for l in f if l.strip()]
    
    print(f"Number of lines: {len(lines)}")
    if len(lines) > 0:
        print(f"Line 0 length: {len(lines[0])}")
        print(f"Line 85 length: {len(lines[-1])}")
        print(f"Line 85 content: {lines[-1]}")

    try:
        # Check basic commuting first
        for i in range(len(lines)):
            s1 = stim.PauliString(lines[i])
            for j in range(i+1, len(lines)):
                s2 = stim.PauliString(lines[j])
                if not s1.commutes(s2):
                    print(f"Anticommutes: {i} vs {j}")
                    # return

        tableau = stim.Tableau.from_stabilizers([stim.PauliString(s) for s in lines], allow_underconstrained=True)
        print(f"Tableau size: {len(tableau)}")
        circuit = tableau.to_circuit(method='graph_state')
        print(f"Circuit num_qubits: {circuit.num_qubits}")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == '__main__':
    check()
