import stim

def solve_task():
    # Read candidate
    with open("candidate_graph.stim", "r") as f:
        content = f.read()
    
    # Replace RX with H
    # RX appears as "RX 0 1 ..."
    # We can just replace "RX" with "H" if it's the first line
    lines = content.splitlines()
    new_lines = []
    for line in lines:
        if line.startswith("RX "):
            new_lines.append(line.replace("RX ", "H "))
        else:
            new_lines.append(line)
    
    new_circuit_text = "\n".join(new_lines)
    c = stim.Circuit(new_circuit_text)
    
    # Check stabilizers
    with open("current_task_stabilizers.txt", "r") as f:
        stabilizers = [stim.PauliString(l.strip()) for l in f if l.strip()]
    
    # To check preservation, we can see if the circuit prepares a state stabilized by S
    # Since the circuit is a Clifford circuit acting on |0>, it prepares a stabilizer state.
    # We can compute the tableau of the circuit and check if it implies the target stabilizers.
    
    t = stim.Tableau.from_circuit(c)
    
    # For each stabilizer S in targets, does T^-1 * S * T stabilizes |0>?
    # i.e., is T^-1 * S * T == +Z_k or product of +Z's?
    # Or simpler: Measure S on the state. Expectation should be +1.
    # Stim's TableauSimulator can peek_observables.
    
    sim = stim.TableauSimulator()
    sim.do_circuit(c)
    
    all_preserved = True
    for i, s in enumerate(stabilizers):
        if i % 10 == 0:
            print(f"Checking stabilizer {i}...")
        exp = sim.peek_observable_expectation(s)
        if exp != 1:
            print(f"Stabilizer {i} NOT preserved. Expectation: {exp}")
            all_preserved = False
            break
    
    if all_preserved:
        print("All stabilizers preserved.")
        
        # Count metrics
        cx = 0
        vol = 0
        for instr in c:
            name = instr.name
            args = instr.targets_copy()
            if name == "CX" or name == "CNOT":
                n = len(args) // 2
                cx += n
                vol += 2 * n
            elif name in ["CZ", "CY", "XC", "YC", "ZC"]:
                n = len(args) // 2
                vol += 2 * n
            else:
                vol += len(args)
        
        print(f"Metrics: CX={cx}, Vol={vol}")
        
        with open("candidate_final.stim", "w") as f:
            f.write(new_circuit_text)
    else:
        print("Verification failed.")

if __name__ == "__main__":
    solve_task()
