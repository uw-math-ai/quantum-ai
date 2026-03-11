import stim

def load_stabilizers(filename):
    with open(filename, 'r') as f:
        lines = [line.strip() for line in f if line.strip()]
    return lines

def count_cx(circuit):
    count = 0
    for instr in circuit:
        if instr.name == "CX" or instr.name == "CNOT":
            count += len(instr.targets_copy()) // 2
    return count

def solve():
    stabilizers = load_stabilizers("current_target_stabilizers.txt")
    
    # Try creating a Tableau from stabilizers
    try:
        t = stim.Tableau.from_stabilizers(stabilizers, allow_underconstrained=True)
    except Exception as e:
        print(f"Error creating tableau: {e}")
        return

    # Synthesize using graph state method (often optimal for clifford states)
    c_graph = t.to_circuit(method="graph_state")
    
    # Convert CZ to CX + H to see CX count
    # Stim's graph state uses H, S, CZ. 
    # CZ(c, t) = H(t) CX(c, t) H(t)
    # We want to count how many CZs are there.
    
    cz_count = 0
    for instr in c_graph:
        if instr.name == "CZ":
            cz_count += len(instr.targets_copy()) // 2
            
    print(f"Graph state circuit has {cz_count} CZ gates.")
    print(f"Equivalent CX count: {cz_count}")
    
    # Write to file
    with open("candidate_graph.stim", "w") as f:
        f.write(str(c_graph))

    # Also try elimination method
    c_elim = t.to_circuit(method="elimination")
    cx_elim = count_cx(c_elim)
    print(f"Elimination circuit has {cx_elim} CX gates.")
    
    with open("candidate_elim.stim", "w") as f:
        f.write(str(c_elim))
        
    # Check baseline
    with open("current_baseline.stim", "r") as f:
        baseline_text = f.read()
    baseline = stim.Circuit(baseline_text)
    print(f"Baseline CX count: {count_cx(baseline)}")

if __name__ == "__main__":
    solve()
