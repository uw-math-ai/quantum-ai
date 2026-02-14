import stim

def solve_circuit():
    with open("target_stabilizers_102.txt", "r") as f:
        stabilizers = [line.strip() for line in f if line.strip()]

    # Create a Tableau from the stabilizers
    # allow_underconstrained=True allows us to proceed even if we have fewer than 102 stabilizers
    # However, to be safe and ensure a valid state preparation, we might want to extend it.
    # But stim might handle it.
    try:
        t = stim.Tableau.from_stabilizers([stim.PauliString(s) for s in stabilizers], allow_underconstrained=True)
    except Exception as e:
        print(f"Error: {e}")
        return

    # The tableau T has the property that it maps Z_k to stabilizer_k.
    # So if we start with |0...0> (which is stabilized by Z_1...Z_n),
    # and apply the unitary U corresponding to T, we get a state stabilized by T Z_k T^dag = stabilizer_k.
    # Wait, let's verify this.
    # A tableau T represents a Clifford operation C.
    # T.z_output(k) gives the Pauli string corresponding to C Z_k C^dag.
    # So if we prepare |0...0>, which is +1 eigenstate of Z_k for all k,
    # then C |0...0> is +1 eigenstate of C Z_k C^dag.
    # stim.Tableau.from_stabilizers constructs T such that T.z_output(k) = stabilizer[k].
    # So applying the circuit form of T to |0...0> should prepare the desired state.
    
    # However, there is a catch. The stabilizers provided might not be Z_0, Z_1, ... in the input.
    # from_stabilizers guarantees that the output Z's match the inputs.
    # But for the underconstrained case, it might pick specific qubits.
    # Let's check which input qubits map to the stabilizers.
    
    # Actually, let's just try generating the circuit and running it against the check tool.
    
    circuit = t.to_circuit("elimination")
    print(circuit)

if __name__ == "__main__":
    solve_circuit()
