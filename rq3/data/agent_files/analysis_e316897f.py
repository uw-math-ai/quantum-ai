import stim
import sys
import os

def analyze():
    print("Starting analysis UUID e316897f...")
    # Load baseline
    try:
        baseline = stim.Circuit.from_file("baseline_task_v100.stim")
    except Exception as e:
        print(f"Error loading baseline: {e}")
        return

    # Count metrics
    cx_count = sum(1 for op in baseline.flattened() if op.name == "CX")
    volume = sum(1 for op in baseline.flattened())
    print(f"Baseline: CX={cx_count}, Volume={volume}")

    # Load stabilizers
    try:
        with open("stabilizers_task_v100.txt", "r") as f:
            lines = [l.strip().replace(',', '') for l in f if l.strip()]
        
        stabilizers = []
        for l in lines:
            if l:
                stabilizers.append(stim.PauliString(l))
        
        print(f"Loaded {len(stabilizers)} stabilizers.")
        if len(stabilizers) > 0:
            print(f"First stabilizer len: {len(stabilizers[0])}")
            
    except Exception as e:
        print(f"Error loading stabilizers: {e}")
        return

    # Check preservation
    sim = stim.TableauSimulator()
    sim.do_circuit(baseline)
    preserved = True
    failed_indices = []
    for i, s in enumerate(stabilizers):
        if sim.peek_observable_expectation(s) != 1:
            preserved = False
            failed_indices.append(i)
    
    print(f"Baseline preserves stabilizers: {preserved}")
    if not preserved:
        print(f"Failed indices: {failed_indices}")

    # Generate tableau
    t = stim.Tableau.from_circuit(baseline)

    # Try graph state synthesis
    try:
        print("Attempting graph state synthesis...")
        graph_circuit = t.to_circuit(method="graph_state")
        
        # Convert CZ to CX + H
        converted = stim.Circuit()
        for op in graph_circuit.flattened():
            if op.name == "CZ":
                targets = op.targets_copy()
                for k in range(0, len(targets), 2):
                    t1 = targets[k]
                    t2 = targets[k+1]
                    # CZ(c, t) = H(t) CX(c, t) H(t)
                    converted.append("H", [t2])
                    converted.append("CX", [t1, t2])
                    converted.append("H", [t2])
            else:
                converted.append(op)
        
        g_cx = sum(1 for op in converted.flattened() if op.name == "CX")
        g_vol = sum(1 for op in converted.flattened())
        print(f"Graph state circuit (converted): CX={g_cx}, Volume={g_vol}")
        
        if g_cx < cx_count:
             print("Graph state is better in CX!")
        elif g_cx == cx_count and g_vol < volume:
             print("Graph state is better in Volume!")
        else:
             print("Graph state is NOT better.")

        with open("candidate_graph_e316897f.stim", "w") as f:
            f.write(str(converted))
            
    except Exception as e:
        print(f"Graph state synthesis failed: {e}")

    # Try elimination synthesis
    try:
        print("Attempting elimination synthesis...")
        elim_circuit = t.to_circuit(method="elimination")
        e_cx = sum(1 for op in elim_circuit.flattened() if op.name == "CX")
        e_vol = sum(1 for op in elim_circuit.flattened())
        print(f"Elimination circuit: CX={e_cx}, Volume={e_vol}")
        
        if e_cx < cx_count:
             print("Elimination is better in CX!")
        elif e_cx == cx_count and e_vol < volume:
             print("Elimination is better in Volume!")
        else:
             print("Elimination is NOT better.")

        with open("candidate_elimination_e316897f.stim", "w") as f:
            f.write(str(elim_circuit))
            
    except Exception as e:
        print(f"Elimination synthesis failed: {e}")

if __name__ == "__main__":
    analyze()
