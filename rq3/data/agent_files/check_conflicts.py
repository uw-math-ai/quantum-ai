import stim

def check_stabilizers():
    with open("stabilizers_task_v4.txt", "r") as f:
        lines = [line.strip().replace(',', '') for line in f if line.strip()]
    
    print(f"Total stabilizers: {len(lines)}")
    lengths = [len(s) for s in lines]
    print(f"Lengths: {set(lengths)}")
    
    # Check consistency
    paulis = [stim.PauliString(s) for s in lines]
    conflicts = []
    for i in range(len(paulis)):
        for j in range(i + 1, len(paulis)):
            if not paulis[i].commutes(paulis[j]):
                conflicts.append((i, j))
                if len(conflicts) < 5:
                    print(f"Conflict: {i} vs {j}")
    
    print(f"Total conflicts: {len(conflicts)}")
    
    # Check which ones the baseline preserves
    baseline = stim.Circuit.from_file("baseline_task_v4.stim")
    sim = stim.TableauSimulator()
    sim.do(baseline)
    
    preserved_indices = []
    failed_indices = []
    for i, p in enumerate(paulis):
        if sim.peek_observable_expectation(p) == 1:
            preserved_indices.append(i)
        else:
            failed_indices.append(i)
            
    print(f"Baseline preserves: {len(preserved_indices)}")
    print(f"Baseline fails: {failed_indices}")
    
    # Check consistency of preserved set
    preserved_paulis = [paulis[i] for i in preserved_indices]
    p_conflicts = 0
    for i in range(len(preserved_paulis)):
        for j in range(i + 1, len(preserved_paulis)):
            if not preserved_paulis[i].commutes(preserved_paulis[j]):
                p_conflicts += 1
    
    print(f"Conflicts in preserved set: {p_conflicts}")

if __name__ == "__main__":
    check_stabilizers()
