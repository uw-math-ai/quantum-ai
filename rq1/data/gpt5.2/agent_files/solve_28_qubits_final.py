import stim

stabilizers = [
    "IIXIXXXIIIIIIIIIIIIIIIIIIIII", 
    "IIIIIIIIIXIXXXIIIIIIIIIIIIII", 
    "IIIIIIIIIIIIIIIIXIXXXIIIIIII", 
    "IIIIIIIIIIIIIIIIIIIIIIIXIXXX", 
    "IXIXIXXIIIIIIIIIIIIIIIIIIIII", 
    "IIIIIIIIXIXIXXIIIIIIIIIIIIII", 
    "IIIIIIIIIIIIIIIXIXIXXIIIIIII", 
    "IIIIIIIIIIIIIIIIIIIIIIXIXIXX", 
    "XXXIIXIIIIIIIIIIIIIIIIIIIIII", 
    "IIIIIIIXXXIIXIIIIIIIIIIIIIII", 
    "IIIIIIIIIIIIIIXXXIIXIIIIIIII", 
    "IIIIIIIIIIIIIIIIIIIIIXXXIIXI", 
    "IIZIZZZIIIIIIIIIIIIIIIIIIIII", 
    "IIIIIIIIIZIZZZIIIIIIIIIIIIII", 
    "IIIIIIIIIIIIIIIIZIZZZIIIIIII", 
    "IIIIIIIIIIIIIIIIIIIIIIIZIZZZ", 
    "IZIZIZZIIIIIIIIIIIIIIIIIIIII", 
    "IIIIIIIIZIZIZZIIIIIIIIIIIIII", 
    "IIIIIIIIIIIIIIIZIZIZZIIIIIII", 
    "IIIIIIIIIIIIIIIIIIIIIIZIZIZZ", 
    "ZZZIIZIIIIIIIIIIIIIIIIIIIIII", 
    "IIIIIIIZZZIIZIIIIIIIIIIIIIII", 
    "IIIIIIIIIIIIIIZZZIIZIIIIIIII", 
    "IIIIIIIIIIIIIIIIIIIIIZZZIIZI", 
    "XXIXIIIXXIXIIIXXIXIIIXXIXIII", 
    "ZZIZIIIZZIZIIIZZIZIIIZZIZIII"
]

print(f"Number of stabilizers: {len(stabilizers)}")
num_qubits = len(stabilizers[0])
print(f"Number of qubits: {num_qubits}")

# Convert to stim.PauliString
stim_stabilizers = [stim.PauliString(s) for s in stabilizers]

try:
    # Create tableau from stabilizers
    # We use allow_underconstrained=True because we have 26 stabilizers for 28 qubits
    # We use allow_redundant=True just in case, though they look independent
    tableau = stim.Tableau.from_stabilizers(stim_stabilizers, allow_underconstrained=True, allow_redundant=True)
    
    # Generate circuit
    circuit = tableau.to_circuit("elimination")
    
    # Verify locally
    sim = stim.TableauSimulator()
    sim.do(circuit)
    
    failed = False
    for i, s in enumerate(stim_stabilizers):
        exp = sim.peek_observable_expectation(s)
        if exp != 1:
            print(f"Stabilizer {i} failed: {s}, Expectation: {exp}")
            failed = True
            
    if not failed:
        print("SUCCESS: Circuit generated and verified locally.")
        with open("circuit_28_final.stim", "w") as f:
            f.write(str(circuit))
    else:
        print("FAILURE: Circuit did not satisfy all stabilizers.")

except Exception as e:
    print(f"Error generating circuit: {e}")
    import traceback
    traceback.print_exc()
