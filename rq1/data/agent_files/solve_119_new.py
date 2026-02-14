import stim

def solve():
    with open('target_stabilizers_119_new.txt', 'r') as f:
        stabs = [line.strip() for line in f if line.strip()]

    # Create tableau from stabilizers
    # allow_underconstrained=True because we might have fewer stabilizers than qubits (logic qubits code)
    stim_stabs = [stim.PauliString(s) for s in stabs]
    tableau = stim.Tableau.from_stabilizers(stim_stabs, allow_underconstrained=True)
    
    # Convert to circuit using elimination
    circuit = tableau.to_circuit("elimination")
    
    # Print the circuit
    print(circuit)

if __name__ == "__main__":
    solve()