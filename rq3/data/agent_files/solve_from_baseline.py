import stim

def get_metrics(circuit):
    cx = 0
    vol = 0
    for instr in circuit:
        n_targets = len(instr.targets_copy())
        if instr.name == "CX":
            n = n_targets // 2
            cx += n
            vol += n
        elif instr.name in ["CY", "CZ", "SWAP", "ISWAP", "ISWAP_DAG"]:
            n = n_targets // 2
            vol += n
        else:
            vol += n_targets
    return cx, vol

def convert_rx_to_h(circuit):
    new_circuit = stim.Circuit()
    for instr in circuit:
        if instr.name == "RX":
            new_circuit.append("H", instr.targets_copy())
        else:
            new_circuit.append(instr)
    return new_circuit

def solve():
    print("Synthesizing from baseline state...")
    
    baseline = stim.Circuit.from_file("data/agent_files/baseline.stim")
    sim = stim.TableauSimulator()
    sim.do(baseline)
    
    # Get canonical stabilizers of the prepared state
    # This returns a list of PauliStrings stabilizing the state
    # There will be 63 stabilizers for 63 qubits (fully specified state).
    # The prompt only listed 62, so this specifies the logical qubit too.
    stabilizers = sim.canonical_stabilizers()
    
    # Synthesize
    # Use elimination to be robust (implements unitary)
    tableau = stim.Tableau.from_stabilizers(stabilizers)
    circuit_e = tableau.to_circuit("elimination")
    
    # Convert CX to H CZ H
    # CX a b = H b CZ a b H b
    candidate = stim.Circuit()
    for instr in circuit_e:
        if instr.name == "CX":
             targets = instr.targets_copy()
             # Iterate pairs
             for i in range(0, len(targets), 2):
                 c = targets[i]
                 t = targets[i+1]
                 # H t
                 candidate.append("H", [t])
                 # CZ c t
                 candidate.append("CZ", [c, t])
                 # H t
                 candidate.append("H", [t])
        else:
            candidate.append(instr)
    
    # Check metrics
    cx, vol = get_metrics(candidate)
    print(f"Candidate: CX={cx}, Vol={vol}")
    
    # Verify against the prompt's stabilizers (subset)
    # Load prompt stabilizers to verify
    with open("data/agent_files/target_stabilizers.txt") as f:
         lines = [line.strip() for line in f if line.strip()]
    prompt_stabs = []
    for line in lines:
        if ". " in line: line = line.split(". ", 1)[1]
        prompt_stabs.append(stim.PauliString(line))
        
    sim2 = stim.TableauSimulator()
    sim2.do(candidate)
    
    valid = True
    for p in prompt_stabs:
        if sim2.peek_observable_expectation(p) != 1:
            valid = False
            break
            
    if valid:
        print("Candidate matches prompt stabilizers!")
        with open("data/agent_files/candidate_from_baseline.stim", "w") as f:
            f.write(str(candidate))
    else:
        print("Candidate MISMATCHES prompt stabilizers!")

if __name__ == "__main__":
    solve()
