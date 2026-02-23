import stim

stabilizers = [
    "XZZXIIIIIIIIIIIIIIII",
    "IIIIIXZZXIIIIIIIIIII",
    "IIIIIIIIIIXZZXIIIIII",
    "IIIIIIIIIIIIIIIXZZXI",
    "IXZZXIIIIIIIIIIIIIII",
    "IIIIIIXZZXIIIIIIIIII",
    "IIIIIIIIIIIXZZXIIIII",
    "IIIIIIIIIIIIIIIIXZZX",
    "XIXZZIIIIIIIIIIIIIII",
    "IIIIIXIXZZIIIIIIIIII",
    "IIIIIIIIIIXIXZZIIIII",
    "IIIIIIIIIIIIIIIXIXZZ",
    "ZXIXZIIIIIIIIIIIIIII",
    "IIIIIZXIXZIIIIIIIIII",
    "IIIIIIIIIIZXIXZIIIII",
    "IIIIIIIIIIIIIIIZXIXZ",
    "XXXXXXXXXXXXXXXXXXXX",
    "ZZZZZZZZZZZZZZZZZZZZ"
]

def solve():
    # Convert strings to PauliStrings
    pauli_stabs = [stim.PauliString(s) for s in stabilizers]
    
    # Generate tableau
    try:
        tableau = stim.Tableau.from_stabilizers(pauli_stabs, allow_underconstrained=True)
    except Exception as e:
        print(f"Error generating tableau: {e}")
        return

    # Convert to circuit
    circuit = tableau.to_circuit("elimination")
    
    # Check if the circuit satisfies the stabilizers
    sim = stim.TableauSimulator()
    sim.do(circuit)
    
    print("Circuit generated.")
    print(circuit)
    
    all_good = True
    for i, s in enumerate(pauli_stabs):
        if not sim.measure_observable(s):
             # measure_observable returns True if +1, False if -1 (wait, no)
             # documentation says: "Returns the result of measuring the observable."
             # "The result is True if the measurement result is -1, and False if the measurement result is +1."
             # Wait, let me double check that.
             pass
    
    # Let's use peek_observable_expectation
    for i, s in enumerate(pauli_stabs):
        expectation = sim.peek_observable_expectation(s)
        if expectation != 1:
            print(f"Stabilizer {i} not satisfied: {stabilizers[i]}, expectation: {expectation}")
            all_good = False
            
    if all_good:
        print("All stabilizers satisfied locally.")
        with open("circuit_20.stim", "w") as f:
            f.write(str(circuit))

solve()
