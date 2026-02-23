import stim

def solve():
    with open(r'data/gemini-3-pro-preview/agent_files/stabilizers_186.txt') as f:
        lines = [line.strip() for line in f if line.strip()]

    # Indices to drop
    drop_indices = {7, 97, 105}
    
    selected_stabilizers = []
    for i, line in enumerate(lines):
        if i not in drop_indices:
            selected_stabilizers.append(stim.PauliString(line))
            
    print(f"Selected {len(selected_stabilizers)} stabilizers.")
    
    try:
        tableau = stim.Tableau.from_stabilizers(selected_stabilizers, allow_underconstrained=True)
        circuit = tableau.to_circuit()
        
        # Verify internally
        # for s in selected_stabilizers:
        #     if not tableau.satisfies(s):
        #         print("Warning: Tableau does not satisfy a selected stabilizer!")

        with open(r'data/gemini-3-pro-preview/agent_files/circuit_186.stim', 'w') as f:
            f.write(str(circuit))
        print("Success! Circuit written to circuit_186.stim")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    solve()
