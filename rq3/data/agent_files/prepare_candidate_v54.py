import stim

def fix_circuit(circuit):
    new_circuit = stim.Circuit()
    for instruction in circuit:
        if instruction.name == "RX":
            # Replace RX with H
            # RX targets are reset to |+>. From |0>, H does this.
            for t in instruction.targets_copy():
                new_circuit.append("H", [t])
        elif instruction.name == "R" or instruction.name == "RZ":
            # Reset to |0>. From |0>, this is Identity.
            pass
        elif instruction.name == "RY":
             # Reset to |i>. From |0>, H then S.
             # H|0> = |+>. S|+> = |i>.
             for t in instruction.targets_copy():
                 new_circuit.append("H", [t])
                 new_circuit.append("S", [t])
        elif instruction.name == "CZ":
            # Convert CZ to CX
            targets = instruction.targets_copy()
            for i in range(0, len(targets), 2):
                c = targets[i]
                t = targets[i+1]
                # CZ(c, t) = H(t) CX(c, t) H(t)
                new_circuit.append("H", [t])
                new_circuit.append("CX", [c, t])
                new_circuit.append("H", [t])
        else:
            new_circuit.append(instruction)
    return new_circuit

def count_metrics(circuit):
    cx_count = 0
    volume = 0
    for instruction in circuit:
        if instruction.name == "CX":
            n = len(instruction.targets_copy()) // 2
            cx_count += n
            volume += n
        elif instruction.name == "CZ":
             n = len(instruction.targets_copy()) // 2
             volume += n
        elif instruction.name in ["H", "S", "S_DAG", "X", "Y", "Z", "I", "SQRT_X", "SQRT_X_DAG", "SQRT_Y", "SQRT_Y_DAG"]:
            volume += len(instruction.targets_copy())
            
    return cx_count, volume

def main():
    print("Loading baseline...")
    with open("current_task_baseline.stim", "r") as f:
        baseline = stim.Circuit(f.read())
        
    sim = stim.TableauSimulator()
    sim.do_circuit(baseline)
    tableau = sim.current_inverse_tableau().inverse()
    
    print("Synthesizing graph state...")
    candidate_graph = tableau.to_circuit(method="graph_state")
    
    print("Fixing circuit (Resets -> Gates, CZ -> CX)...")
    candidate_fixed = fix_circuit(candidate_graph)
    
    cx, vol = count_metrics(candidate_fixed)
    print(f"Fixed Metrics: CX={cx}, Volume={vol}")
    
    # Verify stabilizers
    print("Verifying stabilizers...")
    with open("current_task_stabilizers.txt", "r") as f:
        stabs = [line.strip() for line in f if line.strip()]
        
    sim2 = stim.TableauSimulator()
    sim2.do_circuit(candidate_fixed)
    preserved = 0
    for s in stabs:
        if sim2.peek_observable_expectation(stim.PauliString(s)) == 1:
            preserved += 1
        else:
            print(f"FAILED: {s}")
            
    print(f"Preserved: {preserved}/{len(stabs)}")
    
    if preserved == len(stabs):
        print("Candidate is VALID.")
        with open("candidate_v54_opt.stim", "w") as f:
            f.write(str(candidate_fixed))
        print("Written to candidate_v54_opt.stim")
    else:
        print("Candidate is INVALID.")

if __name__ == "__main__":
    main()
