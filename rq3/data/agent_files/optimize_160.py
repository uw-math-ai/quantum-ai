import stim

def load_stabilizers(filename):
    with open(filename, 'r') as f:
        content = f.read().replace('\n', '').replace(' ', '')
    return [s for s in content.split(',') if s]

def count_cx(circuit):
    return circuit.num_gates("CX")

def main():
    stabilizers = load_stabilizers("target_stabilizers.txt")
    print(f"Loaded {len(stabilizers)} stabilizers.")
    if not stabilizers:
        print("Error: No stabilizers loaded.")
        return

    # Create Tableau from stabilizers
    # stim.Tableau.from_stabilizers creates a tableau T such that T|0> is stabilized by the stabilizers.
    # However, it might require a specific phase. The input strings are Pauli strings (e.g. "XX...").
    # If the phase is not specified, Stim assumes +1.
    
    try:
        tableau = stim.Tableau.from_stabilizers(stabilizers, allow_underconstrained=True)
    except Exception as e:
        print(f"Error creating tableau: {e}")
        return

    # Synthesize using graph state method
    try:
        circuit_graph = tableau.to_circuit(method="graph_state")
        # Convert CZ to CX?
        # A CZ gate is equivalent to H on target, CX, H on target.
        # But wait, CZ is symmetric. 
        # Actually, in graph states, it's just CZs and local Cliffords.
        # If the metric is strictly CX count, and CZ is not CX, I might need to decompose.
        # But usually in these problems, "cx_count" might implicitly allow CZ or I should convert.
        # Let's assume I need to convert CZ to CX.
        # To minimize CX, each CZ becomes 1 CX + H gates.
        # So I will decompose CZ into CX + H.
        # Actually, stim has a decompose method? No, but I can string replace or iterate.
        
        new_circuit = stim.Circuit()
        for instr in circuit_graph:
            if instr.name == "CZ":
                targets = instr.targets_copy()
                for i in range(0, len(targets), 2):
                    c = targets[i]
                    t = targets[i+1]
                    new_circuit.append("H", [t])
                    new_circuit.append("CX", [c, t])
                    new_circuit.append("H", [t])
            elif instr.name == "CX":
                new_circuit.append(instr)
            else:
                new_circuit.append(instr)
        
        # Optimize the new circuit (cancel H gates)
        # stim's circuit.flattened() ...
        # But simple H cancellation is easy.
        
        # Let's use stim's internal methods if possible.
        # But wait, does to_circuit("graph_state") produce CZs? Yes.
        
    except Exception as e:
        print(f"Error synthesizing circuit: {e}")
        return

    # Check baseline
    with open("baseline.stim", "r") as f:
        baseline_text = f.read()
    baseline = stim.Circuit(baseline_text)
    
    print(f"Baseline CX count: {count_cx(baseline)}")
    print(f"New Circuit (raw graph state converted) CX count: {count_cx(new_circuit)}")
    
    # Save candidate
    with open("candidate.stim", "w") as f:
        f.write(new_circuit.to_file(format="stim"))

if __name__ == "__main__":
    main()
