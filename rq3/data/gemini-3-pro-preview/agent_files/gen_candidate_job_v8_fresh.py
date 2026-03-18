import stim

def main():
    # Load baseline
    try:
        with open("baseline_job_v8.stim", "r") as f:
            baseline_text = f.read()
        baseline = stim.Circuit(baseline_text)
    except FileNotFoundError:
        print("Error: baseline_job_v8.stim not found.")
        return

    # Simulate to get tableau
    sim = stim.TableauSimulator()
    sim.do(baseline)
    tableau = sim.current_inverse_tableau().inverse()

    # Generate graph state circuit
    # This produces a circuit that prepares the stabilizer state from |0>
    try:
        candidate = tableau.to_circuit(method="graph_state")
    except Exception as e:
        print(f"Error generating graph state: {e}")
        return

    # Post-process
    new_circuit = stim.Circuit()
    
    # Iterate through instructions
    for instr in candidate:
        name = instr.name
        targets = instr.targets_copy()
        
        # Handle RX (Reset X) -> H (Hadamard on |0>)
        if name == "RX":
            # RX prepares |+> from nothing (reset).
            # H on |0> prepares |+>.
            # Since we assume start at |0>, we use H.
            # But wait, does RX reset the qubit first?
            # If the qubit is already used, RX resets it. H just rotates it.
            # Graph state synthesis assumes it's creating the state from scratch.
            # The output circuit assumes initialized qubits (usually |0>).
            # If it assumes |0>, then RX (Reset X) is redundant if it resets to |+>.
            # But "RX" is specifically "Reset to |+>". 
            # If we replace with H, we assume input is |0>.
            # If input is garbage, H is wrong.
            # But in this optimization task, we are optimizing a full circuit which presumably starts from |0>.
            # So H is correct.
            name = "H"
        
        # Handle R (Reset Z) -> Identity (if start from |0>)
        elif name == "R" or name == "RZ": 
            # R resets to |0>. If already |0>, it's Identity.
            # We can likely skip it.
            continue
            
        # Split instructions to avoid line wrapping and ensure pairwise/singlet handling
        # 2-qubit gates
        if name in ["CZ", "CX", "CNOT", "CY", "SWAP", "ISWAP", "XX", "YY", "ZZ"]:
            for i in range(0, len(targets), 2):
                new_circuit.append(stim.CircuitInstruction(name, targets[i:i+2]))
        # 1-qubit gates
        else:
            for t in targets:
                new_circuit.append(stim.CircuitInstruction(name, [t]))

    # Output
    out_file = "candidate_job_v8_fresh.stim"
    with open(out_file, "w") as f:
        f.write(str(new_circuit))

    print(f"Written to {out_file}")
    print(f"Candidate gates: {len(new_circuit)}")

if __name__ == "__main__":
    main()
