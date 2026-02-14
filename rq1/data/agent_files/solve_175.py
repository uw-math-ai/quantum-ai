import stim

def solve_stabilizers():
    # Read stabilizers from file
    with open(r'C:\Users\anpaz\Repos\quantum-ai\rq1\stabilizers_175.txt', 'r') as f:
        stabilizers = [line.strip() for line in f if line.strip()]

    # Filter out empty lines just in case
    stabilizers = [s for s in stabilizers if s]
    
    num_qubits = len(stabilizers[0])
    
    try:
        # Convert strings to stim.PauliString objects
        stabilizers_ps = [stim.PauliString(s) for s in stabilizers]
        print(f"Number of stabilizers: {len(stabilizers)}")
        
        tableau = stim.Tableau.from_stabilizers(stabilizers_ps, allow_redundant=True, allow_underconstrained=True)
        circuit = tableau.to_circuit()
        
        # Write circuit to file
        with open('circuit.stim', 'w') as f:
            f.write(str(circuit))
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    solve_stabilizers()
