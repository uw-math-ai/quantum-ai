import stim

def count_cx(circuit):
    count = 0
    for op in circuit:
        if op.name == "CX" or op.name == "CNOT":
            count += len(op.targets_copy()) // 2
    return count

def count_volume(circuit):
    # Approximating volume as total gates for now.
    count = 0
    for op in circuit:
        if op.name in ["CX", "CNOT", "CY", "CZ", "H", "S", "S_DAG", "SQRT_X", "SQRT_X_DAG", "SQRT_Y", "SQRT_Y_DAG", "SQRT_Z", "SQRT_Z_DAG", "X", "Y", "Z", "I"]:
             if op.name in ["CX", "CNOT", "CY", "CZ"]:
                 count += len(op.targets_copy()) // 2
             else:
                 count += len(op.targets_copy())
    return count

def get_metrics(circuit):
    return (count_cx(circuit), count_volume(circuit))

with open("baseline.stim", "r") as f:
    baseline_text = f.read()
    baseline = stim.Circuit(baseline_text)

sim = stim.TableauSimulator()
sim.do(baseline)
tableau = sim.current_inverse_tableau().inverse()
stabilizers = tableau.to_stabilizers()

print(f"Baseline Metrics: {get_metrics(baseline)}")

candidates = []

# Strategy 1: Default elimination
try:
    circ_elim = tableau.to_circuit(method="elimination")
    candidates.append(("elimination", circ_elim))
except Exception as e:
    print(f"Elimination failed: {e}")

# Strategy 2: Graph state
try:
    circ_graph = tableau.to_circuit(method="graph_state")
    candidates.append(("graph_state", circ_graph))
except Exception as e:
    print(f"Graph state failed: {e}")

# Strategy 3: Parker's method (if available in this version? Just checking standard methods)
# The `to_circuit` method in recent Stim versions is quite good.

print("\nCandidates:")
for name, circ in candidates:
    m = get_metrics(circ)
    print(f"{name}: {m}")
    if m < get_metrics(baseline):
        print(f"  -> IMPROVEMENT FOUND with {name}")
        with open(f"candidate_{name}.stim", "w") as f:
            f.write(str(circ))
    else:
        print(f"  -> No improvement")

