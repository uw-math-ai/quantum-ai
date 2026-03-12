import stim

def check_stabilizers(circuit, stabilizers):
    sim = stim.TableauSimulator()
    sim.do_circuit(circuit)
    for s in stabilizers:
        if sim.peek_observable_expectation(stim.PauliString(s)) != 1:
            return False
    return True

def synthesize_optimized():
    # Read baseline
    with open('baseline.stim', 'r') as f:
        baseline_text = f.read()
    
    c_base = stim.Circuit(baseline_text)
    sim = stim.TableauSimulator()
    sim.do_circuit(c_base)
    
    # Get the tableau of the state preparation unitary
    tableau = sim.current_inverse_tableau().inverse()
    
    # Synthesize new circuit
    # method="graph_state" produces CZ-based circuits (CX count = 0)
    try:
        c_opt = tableau.to_circuit(method="graph_state")
    except Exception as e:
        print(f"Synthesis failed: {e}")
        return

    # Post-process to replace resets with gates acting on |0>
    new_circuit = stim.Circuit()
    for instruction in c_opt:
        if instruction.name == "RX":
            # Reset to |+>. Since input is |0>, this is H.
            new_circuit.append("H", instruction.targets_copy())
        elif instruction.name == "RY":
             # Reset to |i+>. |0> -> H -> |+> -> S -> |i+>
             new_circuit.append("H", instruction.targets_copy())
             new_circuit.append("S", instruction.targets_copy())
        elif instruction.name == "RZ":
             # Reset to |0>. Since input is |0>, this is Identity.
             pass 
        elif instruction.name == "R":
             # Alias for RZ
             pass
        else:
            new_circuit.append(instruction)
            
    # Read target stabilizers
    with open('target_stabilizers_new.txt', 'r') as f:
        target_stabs = [line.strip() for line in f if line.strip()]

    # Check baseline validity first
    sim_base = stim.TableauSimulator()
    sim_base.do_circuit(c_base)
    base_valid = True
    for i, s in enumerate(target_stabs):
        val = sim_base.peek_observable_expectation(stim.PauliString(s))
        if val != 1:
            print(f"Baseline fails stabilizer {i}: {s} -> Expectation: {val}")
            base_valid = False
            # break # Don't break, see all failures
    
    if not base_valid:
        print("Baseline does not preserve target stabilizers! Proceeding anyway to see if we can fix it.")
        
    # Check if valid
    valid = True
    failed_stab = None
    sim = stim.TableauSimulator()
    sim.do_circuit(new_circuit)
    for i, s in enumerate(target_stabs):
        if sim.peek_observable_expectation(stim.PauliString(s)) != 1:
            valid = False
            failed_stab = i
            break
            
    if valid:
        print("Candidate is VALID.")
        with open('candidate.stim', 'w') as f:
            f.write(str(new_circuit))
        
        # Print metrics
        print(f"Candidate qubits: {new_circuit.num_qubits}")
        print(f"Candidate instructions: {len(new_circuit)}")
    else:
        print(f"Candidate is INVALID. Failed on stabilizer {failed_stab}.")

if __name__ == "__main__":
    synthesize_optimized()
