import stim

# Target stabilizers
targets = [
    "XXIIXXI",
    "XIXIXIX",
    "IIIXXXX",
    "ZZIIZZI",
    "ZIZIZIZ",
    "IIIZZZZ"
]

# Baseline circuit
baseline_str = """
CX 1 0 0 1 1 0
H 0
CX 0 3 0 4
H 1
CX 1 0 1 4 1 6 4 2 2 4 4 2 5 2 6 2 4 3 3 4 4 3
H 3
CX 3 5 3 6 4 5 6 4 6 5 5 6 6 5
"""
baseline = stim.Circuit(baseline_str)

# Analyze baseline
sim = stim.TableauSimulator()
sim.do_circuit(baseline)
# The state is pure, so we can get the canonical tableau
tableau = sim.current_inverse_tableau().inverse()

# Check if baseline satisfies targets
print("Checking baseline against targets...")
for t in targets:
    p = stim.PauliString(t)
    exp = sim.measure_observable(p)
    if exp:  # True means -1 eigenvalue, False means +1
        print(f"Baseline FAILS target {t}: result {exp}")
    else:
        print(f"Baseline PASSES target {t}")

# Synthesize new circuit using graph_state method (optimizes for 0 CX, uses CZ)
print("\nSynthesizing new circuit from tableau...")
try:
    # We want to reproduce the exact state the baseline produces
    # So we use the full tableau of the baseline output
    # Stim's to_circuit can produce graph states
    new_circuit = tableau.to_circuit(method="graph_state")
    
    # Check metrics
    cx_count = str(new_circuit).count("CX")
    cz_count = str(new_circuit).count("CZ")
    print(f"New circuit CX count: {cx_count}")
    print(f"New circuit CZ count: {cz_count}")
    
    print("\nGenerated Circuit:")
    print(new_circuit)
    
    # Verify new circuit
    print("\nVerifying new circuit...")
    sim_new = stim.TableauSimulator()
    sim_new.do_circuit(new_circuit)
    all_pass = True
    for t in targets:
        p = stim.PauliString(t)
        if sim_new.measure_observable(p):
            print(f"New circuit FAILS target {t}")
            all_pass = False
    
    if all_pass:
        print("New circuit PASSES all targets")
    
except Exception as e:
    print(f"Synthesis failed: {e}")
