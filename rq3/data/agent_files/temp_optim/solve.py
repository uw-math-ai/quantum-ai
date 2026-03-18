import stim
import os

def load_stabilizers(path):
    with open(path, 'r') as f:
        lines = [l.strip() for l in f if l.strip()]
    return lines

def get_metrics(circuit):
    cx = 0
    vol = 0
    # Simple metric counting. Adjust if the official tool does something different.
    # The official tool uses 'cx_count' and 'volume'.
    for instr in circuit:
        targets = instr.targets_copy()
        if instr.name == "CX" or instr.name == "CNOT":
            cx += len(targets) // 2
            vol += len(targets) // 2
        elif instr.name == "CZ":
            # If we assume CZ is 1 CX + 2 H, then it's 1 CX + 3 vol?
            # Or if the tool counts CZ as 0 CX.
            # Let's count it as 0 CX for now, but be aware.
            # Volume usually counts 2q gates as 1 or more.
            # Let's just output raw counts for now.
            pass
        
        # Volume: (CX, CY, CZ, H, S, SQRT_X, etc.)
        # This means all these gates count towards volume.
        if instr.name in ["CX", "CNOT", "CY", "CZ", "H", "S", "S_DAG", "SQRT_X", "SQRT_X_DAG", "SQRT_Y", "SQRT_Y_DAG", "SQRT_Z", "SQRT_Z_DAG", "X", "Y", "Z", "I"]:
            if instr.name in ["CX", "CNOT", "CY", "CZ"]:
                 vol += len(targets) // 2
            else:
                 vol += len(targets)
    return cx, vol

def convert_cz_to_cx(circuit):
    # Helper to convert CZ to CX + H to be safe with metrics
    new_circuit = stim.Circuit()
    for instr in circuit:
        if instr.name == "CZ":
            targets = instr.targets_copy()
            for i in range(0, len(targets), 2):
                c = targets[i]
                t = targets[i+1]
                new_circuit.append("H", [t])
                new_circuit.append("CX", [c, t])
                new_circuit.append("H", [t])
        else:
            new_circuit.append(instr)
    return new_circuit

def clean_circuit(circuit):
    # Remove RX if present, replace with H if it's acting on |0>
    # Since we generate from Tableau, it might use RX.
    # Tableau.to_circuit() might output RX, RY, RZ.
    # We should replace RX with H?
    # RZ with nothing?
    # This is risky without knowing the state.
    # But graph_state method usually uses H, S, CZ.
    # If we see RX, it might be a Reset X.
    # The prompt says "Do NOT introduce measurements, resets...".
    # So we must remove them.
    # If the circuit starts from |0>, RX is equivalent to H?
    # No, RX resets to |+>. H|0> -> |+>. So yes.
    new_circuit = stim.Circuit()
    for instr in circuit:
        if instr.name == "RX":
            # Replace with H
            new_circuit.append("H", instr.targets_copy())
        elif instr.name == "R" or instr.name == "RZ":
            # Reset Z. |0> -> |0>. Identity on start.
            pass
        elif instr.name == "RY":
             # Reset Y. |0> -> |i>. 
             # H S |0> -> H |0> -> |+> -> S |+> -> |i>? No.
             # H |0> = |+>. S |+> = (|0> + i|1>). 
             # RY resets to |i+> or |i->.
             # We probably won't see RY in graph state synthesis.
             new_circuit.append(instr)
        else:
            new_circuit.append(instr)
    return new_circuit

def main():
    stabs = load_stabilizers("temp_optim/stabilizers.txt")
    
    # Parse baseline
    with open("temp_optim/baseline.stim", 'r') as f:
        baseline = stim.Circuit(f.read())
    
    print(f"Baseline gates: {len(baseline)}")
    cx, vol = get_metrics(baseline)
    print(f"Baseline CX: {cx}, Vol: {vol}")

    # Create Tableau
    # Note: stabilizers are strings like "XX..."
    # We need to create a Tableau.
    # Since there are 38 stabilizers for 42 qubits, we use allow_underconstrained.
    
    # Stim expects stabilizers as "0: X Z\n1: Z Y..." or a list of strings?
    # from_stabilizers takes a list of PauliStrings.
    
    pauli_stabs = []
    for s in stabs:
        pauli_stabs.append(stim.PauliString(s))
        
    try:
        t = stim.Tableau.from_stabilizers(pauli_stabs, allow_underconstrained=True)
    except Exception as e:
        print(f"Error creating tableau: {e}")
        return

    # Method 1: Graph State
    c_graph = t.to_circuit(method="graph_state")
    c_graph = clean_circuit(c_graph)
    # Convert CZ to CX because we suspect the metric requires it or counts CZ as expensive?
    # Actually, let's generate BOTH: one with CZ (raw) and one decomposed.
    # If the tool counts CZ as 0 CX, the raw one wins.
    # If the tool dislikes CZ, the decomposed one might be good.
    
    c_graph_cz = c_graph.copy()
    c_graph_cx = convert_cz_to_cx(c_graph)

    with open("temp_optim/candidate_graph_cz.stim", 'w') as f:
        f.write(str(c_graph_cz))
        
    with open("temp_optim/candidate_graph_cx.stim", 'w') as f:
        f.write(str(c_graph_cx))

    # Method 2: Elimination
    c_elim = t.to_circuit(method="elimination")
    c_elim = clean_circuit(c_elim)
    with open("temp_optim/candidate_elim.stim", 'w') as f:
        f.write(str(c_elim))
        
    print("Candidates generated.")

    print(f"Graph State (CZ): CX={get_metrics(c_graph_cz)[0]}, Vol={get_metrics(c_graph_cz)[1]}")
    print(f"Graph State (CX): CX={get_metrics(c_graph_cx)[0]}, Vol={get_metrics(c_graph_cx)[1]}")
    print(f"Elimination: CX={get_metrics(c_elim)[0]}, Vol={get_metrics(c_elim)[1]}")

if __name__ == "__main__":
    main()
