import stim

def read_stabilizers(filename):
    with open(filename, 'r') as f:
        lines = [line.strip() for line in f if line.strip()]
    return lines

def main():
    stabilizers = read_stabilizers("target_stabilizers.txt")
    
    # Create tableau from stabilizers
    # stim.Tableau.from_stabilizers expects a list of stim.PauliString
    pauli_strings = [stim.PauliString(s) for s in stabilizers]
    
    try:
        tableau = stim.Tableau.from_stabilizers(pauli_strings, allow_underconstrained=True)
    except Exception as e:
        print(f"Error creating tableau: {e}")
        return

    # Method 1: Graph state synthesis (usually CZ based, convert to CX)
    # This usually produces a circuit that prepares the state from |+> state or something.
    # We need to be careful. `to_circuit` produces a circuit that implements the tableau operation.
    # If we want to PREPARE the state stabilized by these stabilizers, and we start from |0>,
    # we should think about what the tableau represents.
    # Actually, `from_stabilizers` creates a tableau T such that T * Z_k * T^-1 = S_k.
    # So T applied to |0> (stabilized by Z) produces the state stabilized by S_k.
    # So `tableau.to_circuit()` is exactly what we want, applied to |0>.
    
    # Try 'graph_state' method
    try:
        circuit_graph = tableau.to_circuit(method="graph_state")
        # graph_state method uses H, S, CZ, SQRT_X_DAG, etc.
        # We might need to transpile CZ to CX for the metric, although the metric allows volume gates.
        # But CX count is primary.
        # A CZ is 1 CX + Hadamards. A CX is 1 CX.
        # If the metric prefers CX count, we should prefer CXs.
        # However, `graph_state` usually produces a lot of CZs.
        
        # Let's write it to a file
        with open("candidate_graph.stim", "w") as f:
            f.write(str(circuit_graph))
            
    except Exception as e:
        print(f"Error graph_state: {e}")

    # Method 2: Elimination method
    try:
        circuit_elim = tableau.to_circuit(method="elimination")
        with open("candidate_elim.stim", "w") as f:
            f.write(str(circuit_elim))
    except Exception as e:
        print(f"Error elimination: {e}")

if __name__ == "__main__":
    main()
