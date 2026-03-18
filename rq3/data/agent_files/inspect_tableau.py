import stim

def inspect_tableau():
    with open("baseline.stim", "r") as f:
        baseline_text = f.read()
    baseline = stim.Circuit(baseline_text)
    tableau = baseline.to_tableau()
    
    # Check rows for qubit 60
    # x_output(k) returns the Pauli string for X_k
    # z_output(k) returns the Pauli string for Z_k
    
    print(f"Tableau size: {len(tableau)}")
    
    print("X_60 -> ", tableau.x_output(60))
    print("Z_60 -> ", tableau.z_output(60))
    
    # Check if X_60 is just X_60 (identity)
    # If it is identity, it should be +X_60
    
    # Check if there are any non-identity rows above 27
    non_identity_count = 0
    for k in range(28, len(tableau)):
        x_out = tableau.x_output(k)
        z_out = tableau.z_output(k)
        # Identity map: X_k -> X_k, Z_k -> Z_k
        # Construct expected identity Pauli string
        # Actually easier to check if len(x_out) > 1 or x_out[k] != 1?
        # stim.PauliString representation is tricky.
        # But we can just print a few.
        pass

inspect_tableau()
