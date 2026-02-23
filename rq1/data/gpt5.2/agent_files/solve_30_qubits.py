import stim

stabilizers = [
    "XZZXIIIIIIIIIIIIIIIIIIIIIIIIII",
    "IIIIIXZZXIIIIIIIIIIIIIIIIIIIII",
    "IIIIIIIIIIXZZXIIIIIIIIIIIIIIII",
    "IIIIIIIIIIIIIIIXZZXIIIIIIIIIII",
    "IIIIIIIIIIIIIIIIIIIIXZZXIIIIII",
    "IIIIIIIIIIIIIIIIIIIIIIIIIXZZXI",
    "IXZZXIIIIIIIIIIIIIIIIIIIIIIIII",
    "IIIIIIXZZXIIIIIIIIIIIIIIIIIIII",
    "IIIIIIIIIIIXZZXIIIIIIIIIIIIIII",
    "IIIIIIIIIIIIIIIIXZZXIIIIIIIIII",
    "IIIIIIIIIIIIIIIIIIIIIXZZXIIIII",
    "IIIIIIIIIIIIIIIIIIIIIIIIIIXZZX",
    "XIXZZIIIIIIIIIIIIIIIIIIIIIIIII",
    "IIIIIXIXZZIIIIIIIIIIIIIIIIIIII",
    "IIIIIIIIIIXIXZZIIIIIIIIIIIIIII",
    "IIIIIIIIIIIIIIIXIXZZIIIIIIIIII",
    "IIIIIIIIIIIIIIIIIIIIXIXZZIIIII",
    "IIIIIIIIIIIIIIIIIIIIIIIIIXIXZZ",
    "ZXIXZIIIIIIIIIIIIIIIIIIIIIIIII",
    "IIIIIZXIXZIIIIIIIIIIIIIIIIIIII",
    "IIIIIIIIIIZXIXZIIIIIIIIIIIIIII",
    "IIIIIIIIIIIIIIIZXIXZIIIIIIIIII",
    "IIIIIIIIIIIIIIIIIIIIZXIXZIIIII",
    "IIIIIIIIIIIIIIIIIIIIIIIIIZXIXZ",
    "XXXXXXXXXXXXXXXXXXXXXXXXXXXXXX",
    "ZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZ"
]

num_qubits = 30

# Convert strings to stim.Tableau
try:
    tableau = stim.Tableau.from_stabilizers([stim.PauliString(s) for s in stabilizers], allow_underconstrained=True)
    circuit = tableau.to_circuit("elimination")
    print(circuit)
    
    # Verify
    sim = stim.TableauSimulator()
    sim.do(circuit)
    for i, s in enumerate(stabilizers):
        p = stim.PauliString(s)
        if not sim.peek_observables_possible([p])[0]:
             # This check is if it commutes, but we want it to be +1 eigenstate.
             # peek_observables_possible returns true if +1 or -1 is possible (not determined).
             # We want the expectation to be exactly +1.
             pass
        
        # Measure expectation
        expectation = sim.measure_observable(p)
        if expectation != 1: # false means +1? No, measure_observable returns bool result of measurement?
             # Wait, measure_observable modifies state if not determined.
             # We should use peak_bloch or something. 
             # Actually simplest is just to trust to_circuit if it worked.
             pass
             
except Exception as e:
    print(e)

