import stim
import sys

def count_metrics(circuit):
    cx = 0
    vol = 0
    for instr in circuit:
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
    return cx, vol

def solve_task():
    print("Reading stabilizers...")
    try:
        with open("current_task_stabilizers.txt", "r") as f:
            lines = [l.strip() for l in f if l.strip()]
        stabilizers = [stim.PauliString(l) for l in lines]
    except Exception as e:
        print(f"Error reading stabilizers: {e}")
        return

    # Create Tableau
    try:
        t = stim.Tableau.from_stabilizers(stabilizers, allow_redundant=True, allow_underconstrained=True)
        print(f"Tableau created. Size: {len(t)}")
    except Exception as e:
        print(f"Error creating tableau: {e}")
        return

    # Synthesize circuits
    print("Synthesizing graph state circuit...")
    c_graph = t.to_circuit(method="graph_state")
    graph_cx, graph_vol = count_metrics(c_graph)
    print(f"Graph State Circuit: CX={graph_cx}, Vol={graph_vol}")
    
    with open("candidate_graph.stim", "w") as f:
        f.write(str(c_graph))

    print("Synthesizing elimination circuit...")
    c_elim = t.to_circuit(method="elimination")
    elim_cx, elim_vol = count_metrics(c_elim)
    print(f"Elimination Circuit: CX={elim_cx}, Vol={elim_vol}")

    with open("candidate_elim.stim", "w") as f:
        f.write(str(c_elim))
    
    # Save best
    if graph_cx <= elim_cx:
        with open("candidate.stim", "w") as f:
            f.write(str(c_graph))
    else:
        with open("candidate.stim", "w") as f:
            f.write(str(c_elim))

if __name__ == "__main__":
    solve_task()
