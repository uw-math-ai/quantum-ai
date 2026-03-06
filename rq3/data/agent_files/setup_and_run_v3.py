import os

baseline_text = r"""CX 32 0 0 32 32 0
H 0 5 6 7
CX 0 5 0 6 0 7 0 8 0 12 0 33 0 34 0 35
H 4 32
CX 4 0 32 0 8 1 1 8 8 1 4 1 32 1 12 2 2 12 12 2 4 2 32 2 16 3 3 16 16 3 3 20 3 33 32 3 32 4 4 32 32 4 4 20 20 5 5 20 20 5 32 6 6 32 32 6 6 24 6 28 24 7 7 24 24 7 28 8 8 28 28 8 20 9 9 20 20 9 9 13 9 20 9 33 9 34
H 28
CX 28 9 20 10 10 20 20 10 28 10 13 11 11 13 13 11 28 11 28 12 12 28 28 12 12 17 12 21 17 13 13 17 17 13 21 14 14 21 21 14 29 15 15 29 29 15 15 25 15 33 34 15 25 16 16 25 25 16 34 16 34 17 17 34 34 17 17 33 32 18 18 32 32 18 18 20 18 21 18 33
H 28
CX 28 18 20 19 19 20 20 19 28 19 21 20 20 21 21 20 28 20 28 21 21 28 28 21 21 22 21 32 32 22 22 32 32 22 32 23 23 32 32 23 33 24 24 33 33 24 24 26 24 30 31 24 35 24 26 25 25 26 26 25 31 25 35 25 30 26 26 30 30 26 31 26 35 26 33 27 27 33 33 27 27 29 27 34 27 35
H 30
CX 30 27 34 28 28 34 34 28 30 28 30 29 30 32 30 34 34 31 31 34 34 31 34 33 33 34 34 33 33 34 35 33 35 34
"""

stabilizers_text = r"""XXXXXXIIIIIIIIIIIIIIIIIIIIIIIIIIIIII
IIIIIIIIIXXXXXXIIIIIIIIIIIIIIIIIIIII
IIIIIIIIIIIIIIIIIIXXXXXXIIIIIIIIIIII
IIIIIIIIIIIIIIIIIIIIIIIIIIIXXXXXXIII
XXXIIIXXXIIIIIIIIIIIIIIIIIIIIIIIIIII
IIIIIIIIIXXXIIIXXXIIIIIIIIIIIIIIIIII
IIIIIIIIIIIIIIIIIIXXXIIIXXXIIIIIIIII
IIIIIIIIIIIIIIIIIIIIIIIIIIIXXXIIIXXX
ZZIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIII
IIIIIIIIIZZIIIIIIIIIIIIIIIIIIIIIIIII
IIIIIIIIIIIIIIIIIIZZIIIIIIIIIIIIIIII
IIIIIIIIIIIIIIIIIIIIIIIIIIIZZIIIIIII
ZIZIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIII
IIIIIIIIIZIZIIIIIIIIIIIIIIIIIIIIIIII
IIIIIIIIIIIIIIIIIIZIZIIIIIIIIIIIIIII
IIIIIIIIIIIIIIIIIIIIIIIIIIIZIZIIIIII
IIIZZIIIIIIIIIIIIIIIIIIIIIIIIIIIIIII
IIIIIIIIIIIIZZIIIIIIIIIIIIIIIIIIIIII
IIIIIIIIIIIIIIIIIIIIIZZIIIIIIIIIIIII
IIIIIIIIIIIIIIIIIIIIIIIIIIIIIIZZIIII
IIIZIZIIIIIIIIIIIIIIIIIIIIIIIIIIIIII
IIIIIIIIIIIIZIZIIIIIIIIIIIIIIIIIIIII
IIIIIIIIIIIIIIIIIIIIIZIZIIIIIIIIIIII
IIIIIIIIIIIIIIIIIIIIIIIIIIIIIIZIZIII
IIIIIIZZIIIIIIIIIIIIIIIIIIIIIIIIIIII
IIIIIIIIIIIIIIIZZIIIIIIIIIIIIIIIIIII
IIIIIIIIIIIIIIIIIIIIIIIIZZIIIIIIIIII
IIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIZZI
IIIIIIZIZIIIIIIIIIIIIIIIIIIIIIIIIIII
IIIIIIIIIIIIIIIZIZIIIIIIIIIIIIIIIIII
IIIIIIIIIIIIIIIIIIIIIIIIZIZIIIIIIIII
IIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIZIZ
XXXIIIIIIXXXIIIIIIXXXIIIIIIXXXIIIIII
ZIIZIIZIIZIIZIIZIIZIIZIIZIIZIIZIIZII
"""

analysis_script = r"""
import stim
import sys

def count_cx(circuit):
    count = 0
    for op in circuit:
        if op.name == "CX":
            count += len(op.targets_copy()) // 2
    return count

def count_volume(circuit):
    # Volume is total gate count in volume gate set
    # Count all targets of all gates in volume set
    # Assuming all gates in circuit are in volume set
    count = 0
    for op in circuit:
        if op.name in ["CX", "CY", "CZ", "H", "S", "SQRT_X", "SQRT_Y", "SQRT_Z", "X", "Y", "Z", "I", "S_DAG", "SQRT_X_DAG", "SQRT_Y_DAG", "SQRT_Z_DAG"]:
            count += len(op.targets_copy())
            if op.name in ["CX", "CY", "CZ"]:
                # These are 2 qubit gates, but len(targets) counts qubits.
                # A CX on 2 qubits counts as 1 gate or 2?
                # Usually volume counts 2-qubit gates as 1?
                # "volume – total gate count in the volume gate set"
                # If I have CX 0 1, is that 1 gate? Yes.
                # If I have CX 0 1 2 3, is that 2 gates? Yes.
                # So for 2-qubit gates, count = len(targets) / 2
                pass
    
    # Let's verify what 'volume' means. Usually it's just number of gates.
    # Stim's `num_gates` does this? No.
    # Let's count operations.
    vol = 0
    for op in circuit:
        if op.name in ["CX", "CY", "CZ"]:
            vol += len(op.targets_copy()) // 2
        elif op.name in ["H", "S", "SQRT_X", "SQRT_Y", "SQRT_Z", "X", "Y", "Z", "I", "S_DAG", "SQRT_X_DAG", "SQRT_Y_DAG", "SQRT_Z_DAG"]:
            vol += len(op.targets_copy())
    return vol

def load_stabilizers(filename):
    with open(filename, 'r') as f:
        lines = [l.strip() for l in f if l.strip()]
    stabilizers = []
    for line in lines:
        line = line.replace(',', '')
        stabilizers.append(stim.PauliString(line))
    return stabilizers

def verify_stabilizers(circuit, stabilizers):
    sim = stim.TableauSimulator()
    sim.do_circuit(circuit)
    for stab in stabilizers:
        if sim.peek_observable_expectation(stab) != 1:
            return False
    return True

def convert_cz_to_cx(circuit):
    new_circuit = stim.Circuit()
    for op in circuit:
        if op.name == "CZ":
            targets = op.targets_copy()
            for i in range(0, len(targets), 2):
                t1 = targets[i]
                t2 = targets[i+1]
                # CZ 0 1 = H 1 CX 0 1 H 1
                new_circuit.append("H", [t2])
                new_circuit.append("CX", [t1, t2])
                new_circuit.append("H", [t2])
        else:
            new_circuit.append(op)
    return new_circuit

def main():
    print("Reading baseline...")
    with open("baseline.stim", "r") as f:
        baseline = stim.Circuit(f.read())
    
    base_cx = count_cx(baseline)
    base_vol = count_volume(baseline)
    print(f"Baseline: CX={base_cx}, Vol={base_vol}")
    
    stabilizers = load_stabilizers("stabilizers.txt")
    
    # Method 1: Elimination
    print("Trying elimination synthesis...")
    tableau = stim.Tableau.from_stabilizers(stabilizers, allow_underconstrained=True)
    circ_elim = tableau.to_circuit(method="elimination")
    
    cx_elim = count_cx(circ_elim)
    vol_elim = count_volume(circ_elim)
    print(f"Elimination: CX={cx_elim}, Vol={vol_elim}")
    
    # Method 2: Graph State
    print("Trying graph state synthesis...")
    circ_graph = tableau.to_circuit(method="graph_state")
    
    # Convert CZ to CX
    circ_graph_cx = convert_cz_to_cx(circ_graph)
    
    cx_graph = count_cx(circ_graph_cx)
    vol_graph = count_volume(circ_graph_cx)
    print(f"Graph State (Converted): CX={cx_graph}, Vol={vol_graph}")
    
    # Check if Elimination is better than Baseline
    elim_is_better = False
    if cx_elim < base_cx:
        elim_is_better = True
    elif cx_elim == base_cx and vol_elim < base_vol:
        elim_is_better = True
        
    # Check if Graph is better than Baseline
    graph_is_better = False
    if cx_graph < base_cx:
        graph_is_better = True
    elif cx_graph == base_cx and vol_graph < base_vol:
        graph_is_better = True
        
    print(f"Elimination better? {elim_is_better}")
    print(f"Graph better? {graph_is_better}")
    
    best_circuit = None
    
    if elim_is_better and graph_is_better:
        # Pick the one that is better between them
        if cx_graph < cx_elim:
            best_circuit = circ_graph_cx
            print("Graph wins")
        elif cx_graph == cx_elim and vol_graph < vol_elim:
             best_circuit = circ_graph_cx
             print("Graph wins")
        else:
             best_circuit = circ_elim
             print("Elim wins")
    elif elim_is_better:
        best_circuit = circ_elim
        print("Elim wins")
    elif graph_is_better:
        best_circuit = circ_graph_cx
        print("Graph wins")
    
    if best_circuit:
        with open("candidate.stim", "w") as f:
            f.write(str(best_circuit))
        print("Saved best candidate.")
    else:
        print("No improvement.")
        
    with open("candidate_elim.stim", "w") as f:
        f.write(str(circ_elim))
    
    with open("candidate_graph_converted.stim", "w") as f:
        f.write(str(circ_graph_cx))

if __name__ == "__main__":
    main()
"""

with open("baseline.stim", "w") as f:
    f.write(baseline_text)

with open("stabilizers.txt", "w") as f:
    f.write(stabilizers_text)

with open("analyze_and_optimize.py", "w") as f:
    f.write(analysis_script)

print("Files created.")
