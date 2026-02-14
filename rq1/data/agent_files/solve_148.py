import stim

def solve():
    with open("stabilizers_148.txt", "r") as f:
        lines = [line.strip() for line in f if line.strip()]

    print(f"Number of stabilizers: {len(lines)}")
    stabilizers = [stim.PauliString(line) for line in lines]
    
    num_qubits = len(stabilizers[0])
    print(f"Number of qubits: {num_qubits}")

    if len(stabilizers) != num_qubits:
        print(f"Warning: Number of stabilizers ({len(stabilizers)}) does not match number of qubits ({num_qubits}).")
        # If fewer stabilizers, we might need to complete the set or it is a code state (not unique).
        # But prompt says "stabilizer state defined by these generators", usually implies a unique state or we just pick one.
        # If we just need *a* state stabilized by these, we can complete the tableau.
    
    try:
        # stim.Tableau.from_stabilizers takes a list of PauliStrings.
        # It expects a full set of stabilizers for a state.
        # If the list is incomplete, this might fail or we might need another method.
        # Let's try.
        tableau = stim.Tableau.from_stabilizers(stabilizers)
        circuit = tableau.to_circuit()
        
        # Save circuit to file
        with open("circuit_148.stim", "w") as f:
            f.write(str(circuit))
        print("Circuit generated successfully.")
        
    except Exception as e:
        print(f"Error generating tableau from stabilizers: {e}")
        # If direct method fails, we might need to use Gaussian elimination manually
        # to find a Clifford that maps Z basis to these stabilizers.

if __name__ == "__main__":
    solve()
