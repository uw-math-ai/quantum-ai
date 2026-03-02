import stim
import sys

def solve_circuit(stabilizers_file):
    with open(stabilizers_file, 'r') as f:
        stabilizers = [line.strip() for line in f if line.strip()]

    num_qubits = len(stabilizers[0])
    
    # Create the tableau from stabilizers
    # We want to find a Clifford operation C such that C|0> is the stabilizer state.
    # stim.Tableau.from_stabilizers can find a tableau that maps Z basis to the target stabilizers.
    try:
        stim_stabilizers = [stim.PauliString(s) for s in stabilizers]
        tableau = stim.Tableau.from_stabilizers(stim_stabilizers, allow_underconstrained=True)
    except Exception as e:
        print(f"Error creating tableau: {e}")
        return

    # The tableau T represents the operation U that prepares the state if we apply it to Z-basis states?
    # Actually, T.to_circuit() gives the circuit that implements the Clifford operation.
    # If T maps Z_i to S_i, then applying T to |0> (stabilized by Z_i) prepares the state stabilized by S_i.
    
    circuit = tableau.to_circuit()
    print(circuit)

if __name__ == "__main__":
    solve_circuit("data/gemini-3-pro-preview/agent_files/stabilizers_36.txt")
