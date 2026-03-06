import stim
import sys

def count_cx(circuit):
    count = 0
    for op in circuit:
        if op.name == "CX" or op.name == "CNOT":
            count += len(op.targets_copy()) // 2
        elif op.name == "CZ":
            count += len(op.targets_copy()) // 2
    return count

def load_stabilizers(filename):
    with open(filename, 'r') as f:
        lines = [line.strip() for line in f if line.strip()]
    # Parse stabilizers
    stabilizers = []
    for line in lines:
        stabilizers.append(stim.PauliString(line))
    return stabilizers

def verify_stabilizers(circuit, stabilizers):
    # Tableau simulation
    sim = stim.TableauSimulator()
    sim.do(circuit)
    
    # Check each stabilizer
    for stab in stabilizers:
        if sim.peek_observable_expectation(stab) != 1:
            return False
    return True

def synthesize_from_tableau(stabilizers):
    # Create a Tableau from the stabilizers
    # This assumes the stabilizers form a complete set or we can extend them?
    # Actually, stim.Tableau.from_stabilizers is what we want
    try:
        tableau = stim.Tableau.from_stabilizers(stabilizers, allow_underconstrained=True)
        # Convert to circuit using graph state method which is often efficient for CX count
        # method='graph_state' usually produces H and CZ gates.
        # We can then decompose CZ to CX.
        # However, CZ count is the metric for graph state.
        # 1 CZ = 1 CX + 2 H (or just 1 CX if we have H's around).
        # Let's try 'elimination' as well.
        
        circuit_graph = tableau.to_circuit(method="graph_state")
        circuit_elim = tableau.to_circuit(method="elimination")
        
        return [circuit_graph, circuit_elim]
    except Exception as e:
        print(f"Synthesis failed: {e}")
        return []

def convert_cz_to_cx(circuit):
    # Convert CZ to CX + H
    # CZ a b = H b CX a b H b
    # But we want to optimize.
    # Actually, let's just do a naive conversion and rely on the fact that graph states are efficient.
    # Or better: CZ 0 1 is equivalent to CX 0 1 surrounded by basis changes.
    # stim has no direct CZ->CX conversion in python API easily without manual replacement.
    # But let's look at the circuit.
    
    new_circuit = stim.Circuit()
    for op in circuit:
        if op.name == "CZ":
            targets = op.targets_copy()
            for i in range(0, len(targets), 2):
                t1 = targets[i]
                t2 = targets[i+1]
                # CZ t1 t2 = H t2 CX t1 t2 H t2
                new_circuit.append("H", [t2])
                new_circuit.append("CX", [t1, t2])
                new_circuit.append("H", [t2])
        else:
            new_circuit.append(op)
    return new_circuit

def main():
    baseline_path = "my_baseline.stim"
    stabilizers_path = "my_stabilizers.txt"
    
    with open(baseline_path, 'r') as f:
        baseline_text = f.read()
    baseline = stim.Circuit(baseline_text)
    
    stabilizers = load_stabilizers(stabilizers_path)
    
    print(f"Baseline CX count: {count_cx(baseline)}")
    
    if not verify_stabilizers(baseline, stabilizers):
        print("WARNING: Baseline does not preserve stabilizers!")
    else:
        print("Baseline preserves stabilizers.")

    print(f"Number of qubits in stabilizers: {len(stabilizers[0])}")
    
    candidates = synthesize_from_tableau(stabilizers)
    
    best_circuit = None
    min_cx = count_cx(baseline)
    
    print(f"Generated {len(candidates)} candidates.")
    
    for i, cand in enumerate(candidates):
        # Convert CZ to CX if needed (graph state output uses CZ)
        # Check if it has CZ
        has_cz = any(op.name == "CZ" for op in cand)
        if has_cz:
            cand = convert_cz_to_cx(cand)
            
        cx = count_cx(cand)
        print(f"Candidate {i} CX count: {cx}")
        
        if verify_stabilizers(cand, stabilizers):
            if cx < min_cx:
                min_cx = cx
                best_circuit = cand
                print(f"Found better candidate! CX: {cx}")
            elif cx == min_cx:
                # Compare volume/length if needed, but for now just note it
                print(f"Found equal candidate. CX: {cx}")
                if best_circuit is None:
                     best_circuit = cand # Fallback if equal
        else:
            print(f"Candidate {i} failed verification.")

    if best_circuit:
        print("\nBest candidate found:")
        print(best_circuit)
        with open("candidate.stim", "w") as f:
            f.write(str(best_circuit))
    else:
        print("No strictly better candidate found. Saving baseline as candidate.")
        with open("candidate.stim", "w") as f:
            f.write(str(baseline))

if __name__ == "__main__":
    main()
