import stim

def solve_underconstrained():
    # Use the fixed final file with 152 lines
    path = r'data\gemini-3-pro-preview\agent_files\stabilizers_fixed_final.txt'
    with open(path, 'r') as f:
        lines = [line.strip() for line in f if line.strip()]

    print(f"Loaded {len(lines)} stabilizers.")
    
    # We expect 153 qubits.
    # If 152 stabilizers, we have 1 logical qubit.
    # We can just generate a circuit that prepares a state in the +1 subspace.
    
    stabs = [stim.PauliString(line) for line in lines]
    
    # Check consistency again just in case
    tableau = stim.Tableau.from_stabilizers(stabs, allow_redundant=False, allow_underconstrained=True)
    print("Tableau created successfully (underconstrained).")
    
    circuit = tableau.to_circuit("elimination")
    
    out_path = r'data\gemini-3-pro-preview\agent_files\circuit_underconstrained.stim'
    with open(out_path, 'w') as f:
        f.write(str(circuit))
        
    print(f"Circuit saved to {out_path}")

if __name__ == "__main__":
    solve_underconstrained()
