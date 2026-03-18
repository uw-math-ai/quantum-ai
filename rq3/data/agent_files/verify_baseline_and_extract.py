import stim

def verify_baseline():
    # Read baseline circuit
    with open("baseline.stim", "r") as f:
        baseline_text = f.read()
    
    circuit = stim.Circuit(baseline_text)
    
    # Compute tableau of baseline
    # Assuming standard initialization |00...0>
    sim = stim.TableauSimulator()
    sim.do_circuit(circuit)
    
    # Check target stabilizers
    with open("target_stabilizers_v10.txt", "r") as f:
        targets = [line.strip() for line in f if line.strip()]

    # Check each target
    preserved_count = 0
    failed_count = 0
    for t_str in targets:
        p = stim.PauliString(t_str)
        # Check expectation value
        # measure_expectation returns +1, -1, or 0
        exp = sim.peek_observable_expectation(p)
        if exp == 1:
            preserved_count += 1
        else:
            failed_count += 1
            # print(f"Failed: {t_str} exp={exp}")

    print(f"Baseline preserved: {preserved_count}/{len(targets)}")
    print(f"Baseline failed: {failed_count}/{len(targets)}")
    
    # Also extract stabilizers from the simulator state
    # This gives us a consistent set of generators for the state
    tableau = sim.current_inverse_tableau().inverse()
    # But current_inverse_tableau gives operation.
    # We want state stabilizers.
    # The state is |0> evolved by circuit.
    # Stabilizers of |0> are Z0, Z1, ...
    # Evolved stabilizers are U Z_i U^dagger.
    # tableau(Z_i) gives the i-th stabilizer.
    
    extracted_stabilizers = []
    num_qubits = len(tableau)
    for i in range(num_qubits):
        extracted_stabilizers.append(str(tableau.z_output(i)))
        
    # Write extracted to file
    with open("extracted_stabilizers.txt", "w") as f:
        for s in extracted_stabilizers:
            f.write(s + "\n")
            
    print(f"Extracted {len(extracted_stabilizers)} stabilizers from baseline.")

if __name__ == "__main__":
    verify_baseline()
