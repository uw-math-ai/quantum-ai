import stim

def debug_stabilizers():
    with open(r'C:\Users\anpaz\Repos\quantum-ai\rq1\data\gemini-3-pro-preview\agent_files\stabilizers_81_qubits.txt', 'r') as f:
        lines = [line.strip() for line in f if line.strip()]
    
    print(f"Number of lines: {len(lines)}")
    lengths = [len(l) for l in lines]
    print(f"Max length: {max(lengths)}")
    print(f"Min length: {min(lengths)}")
    
    # Check for invalid characters
    valid_chars = set('IXYZ')
    for i, l in enumerate(lines):
        if len(l) != 81:
            print(f"Line {i} has length {len(l)}: '{l}'")
            
    # Create a tableau from just the first stabilizer to see num_qubits
    t1 = stim.Tableau.from_stabilizers([stim.PauliString(lines[0])], allow_underconstrained=True)
    print(f"Tableau from first stabilizer num qubits: {len(t1)}")
    
    # Create from all
    t_all = stim.Tableau.from_stabilizers([stim.PauliString(s) for s in lines], allow_underconstrained=True)
    print(f"Tableau from all stabilizers num qubits: {len(t_all)}")

if __name__ == "__main__":
    debug_stabilizers()
