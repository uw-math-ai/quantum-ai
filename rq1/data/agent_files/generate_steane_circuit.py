import stim

def solve():
    # Stabilizers from prompt
    base_stabilizers = [
        "XXIIXXI",
        "XIXIXIX",
        "IIIXXXX",
        "ZZIIZZI",
        "ZIZIZIZ",
        "IIIZZZZ"
    ]
    
    # Add Logical Z to define Logical |0>
    # Z_L = ZZZZZZZ (transversal Z)
    stabilizers = base_stabilizers + ["ZZZZZZZ"]
    
    try:
        tableau = stim.Tableau.from_stabilizers([stim.PauliString(s) for s in stabilizers])
    except ValueError as e:
        print(f"Error creating tableau: {e}")
        # Try finding a valid set of independent stabilizers if the above fails
        # It's possible ZZZZZZZ is dependent or inconsistent?
        # Let's check consistency.
        return

    # Generate circuit
    # method="graph_state" uses H, S, CZ, CX, etc. on the same qubits.
    # It starts from |+> usually, so it adds H at the beginning.
    # But let's check.
    circuit = tableau.to_circuit(method="graph_state")
    
    # Replace RX with H since we start with |0>
    circuit_str = str(circuit).replace("RX", "H")
    print(circuit_str)

if __name__ == "__main__":
    solve()
