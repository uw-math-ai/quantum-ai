import stim

def main():
    # Load stabilizers
    with open("data/agent_files/stabilizers.txt", "r") as f:
        targets = [line.strip() for line in f if line.strip()]
        
    print(f"Loaded {len(targets)} stabilizers.")
    
    # Create Tableau from stabilizers
    # stim.Tableau.from_stabilizers expects a list of PauliStrings.
    # It returns a tableau T such that T(Z_k) = stabilizer[k].
    # Wait, the number of stabilizers must match number of qubits?
    # The baseline has 47 qubits?
    # Let's check baseline qubits.
    
    baseline = stim.Circuit.from_file("data/agent_files/baseline.stim")
    n = baseline.num_qubits
    print(f"Baseline qubits: {n}")
    
    # The stabilizers file has 44 stabilizers.
    # If n > 44, the state is not fully stabilized?
    # Or maybe there are implicit Z stabilizers?
    # The prompt says "Target stabilizers (must all be preserved)".
    # If I use `from_stabilizers`, I need N independent stabilizers.
    # If I have fewer, I can pad with Z_k?
    # Or I can use `from_conjugated_generators`? No.
    
    # Let's check if 44 == n.
    if len(targets) < n:
        print(f"Warning: fewer stabilizers ({len(targets)}) than qubits ({n}).")
        # I need to complete the stabilizer set to fully specify the state?
        # Or can I leave some degrees of freedom?
        # Stim's `from_stabilizers` requires N stabilizers.
        # If I want to optimize for specific stabilizers, I should add dummy stabilizers for the rest?
        # If I add Z on the unused qubits, it assumes they are |0>.
        # Is that safe?
        # The baseline circuit might entangle them?
        # If the target stabilizers don't specify them, maybe their state doesn't matter?
        # "Target stabilizers (must all be preserved)" implies these are the ONLY constraints.
        # BUT `evaluate_optimization` might check only these.
        # However, if I produce a circuit that has fewer CXs but leaves some qubits in |+> instead of |0>, is that better?
        # Yes, strictly better.
        # But `stim` needs a full tableau to synthesize.
        # So I should pick the simplest completion.
        # Z stabilizers on the remaining qubits is the simplest (requires 0 gates usually).
        pass

    # Convert strings to PauliStrings
    paulis = [stim.PauliString(t) for t in targets]
    
    # If len(paulis) < n, we need to add more.
    # We should add Z_i for i not involved?
    # Or just Z_k for k=len(paulis)..n-1?
    # The `from_stabilizers` method creates a tableau of size len(stabilizers)?
    # No, it likely infers size from the PauliStrings.
    # Let's see.
    
    try:
        tableau = stim.Tableau.from_stabilizers(paulis, allow_redundant=False, allow_underconstrained=True)
        # allow_underconstrained=True allows fewer stabilizers than qubits.
        # It will fill the rest with Z's?
        
        circuit = tableau.to_circuit()
        print(f"Synthesized from stabilizers CX count: {count_cx(circuit)}")
        
        # Save
        with open("data/agent_files/candidate_stabilizers.stim", "w") as f:
            f.write(str(circuit))
            
        # Verify
        sim = stim.TableauSimulator()
        sim.do_circuit(circuit)
        preserved = 0
        for p in paulis:
            if sim.peek_observable_expectation(p) == 1:
                preserved += 1
        print(f"Preserved: {preserved}/{len(paulis)}")
        
    except Exception as e:
        print(f"Error synthesizing: {e}")

def count_cx(circuit):
    count = 0
    for instruction in circuit:
        if instruction.name == "CX" or instruction.name == "CNOT":
            count += len(instruction.targets_copy()) // 2
    return count

if __name__ == "__main__":
    main()
