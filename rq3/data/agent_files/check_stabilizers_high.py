import stim

def check_stabilizers():
    with open("baseline.stim", "r") as f:
        baseline_text = f.read()
    baseline = stim.Circuit(baseline_text)
    tableau = baseline.to_tableau()
    
    trivial_count = 0
    non_trivial = []
    
    for k in range(28, len(tableau)):
        z_out = tableau.z_output(k)
        # Check if z_out is exactly +Z_k
        # Construct expected Z_k string
        expected = stim.PauliString(len(tableau))
        expected[k] = 3 # 3 is Z
        
        if z_out == expected:
            trivial_count += 1
        else:
            non_trivial.append((k, str(z_out)))
            
    print(f"Trivial count (Z_k -> Z_k): {trivial_count}")
    print(f"Non-trivial count: {len(non_trivial)}")
    if len(non_trivial) > 0:
        print("Example non-trivial:", non_trivial[0])

check_stabilizers()
