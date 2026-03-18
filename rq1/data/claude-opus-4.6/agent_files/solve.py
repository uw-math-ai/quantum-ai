import stim

# Define the 26 stabilizers for 28 qubits
stabilizers = [
    "XXIIXXIIIIIIIIIIIIIIIIIIIIII",
    "IIIIIIIXXIIXXIIIIIIIIIIIIIII",
    "IIIIIIIIIIIIIIXXIIXXIIIIIIII",
    "IIIIIIIIIIIIIIIIIIIIIXXIIXXI",
    "XIXIXIXIIIIIIIIIIIIIIIIIIIII",
    "IIIIIIIXIXIXIXIIIIIIIIIIIIII",
    "IIIIIIIIIIIIIIXIXIXIXIIIIIII",
    "IIIIIIIIIIIIIIIIIIIIIXIXIXIX",
    "IIIXXXXIIIIIIIIIIIIIIIIIIIII",
    "IIIIIIIIIIXXXXIIIIIIIIIIIIII",
    "IIIIIIIIIIIIIIIIIXXXXIIIIIII",
    "IIIIIIIIIIIIIIIIIIIIIIIIXXXX",
    "ZZIIZZIIIIIIIIIIIIIIIIIIIIII",
    "IIIIIIIZZIIZZIIIIIIIIIIIIIII",
    "IIIIIIIIIIIIIIZZIIZZIIIIIIII",
    "IIIIIIIIIIIIIIIIIIIIIZZIIZZI",
    "ZIZIZIZIIIIIIIIIIIIIIIIIIIII",
    "IIIIIIIZIZIZIZIIIIIIIIIIIIII",
    "IIIIIIIIIIIIIIZIZIZIZIIIIIII",
    "IIIIIIIIIIIIIIIIIIIIIZIZIZIZ",
    "IIIZZZZIIIIIIIIIIIIIIIIIIIII",
    "IIIIIIIIIIZZZZIIIIIIIIIIIIII",
    "IIIIIIIIIIIIIIIIIZZZZIIIIIII",
    "IIIIIIIIIIIIIIIIIIIIIIIIZZZZ",
    "XXXIIIIXXXIIIIXXXIIIIXXXIIII",
    "ZZZIIIIZZZIIIIZZZIIIIZZZIIII",
]

print(f"Number of stabilizers: {len(stabilizers)}")
print(f"Length of each: {len(stabilizers[0])}")

# Use Stim's Tableau to synthesize the circuit
stim_stabs = []
for s in stabilizers:
    stim_stabs.append(stim.PauliString(s))

print("Creating tableau...")
try:
    tableau = stim.Tableau.from_stabilizers(stim_stabs, allow_redundant=True, allow_underconstrained=True)
    print("Tableau created successfully")
    
    # Use graph_state method for CZ-based circuit (CX=0)
    circuit = tableau.to_circuit(method="graph_state")
    print(f"Circuit generated with {len(circuit)} instructions")
    
    # Convert RX to H (since we start from |0⟩, H gives us |+⟩)
    circuit_str = str(circuit)
    circuit_str = circuit_str.replace("RX ", "H ")
    
    # Parse and clean up the circuit
    cleaned_circuit = stim.Circuit(circuit_str)
    print("\nCleaned circuit:")
    print(cleaned_circuit)
    
    # Save to file
    with open("candidate.stim", "w") as f:
        f.write(str(cleaned_circuit))
    print("\nSaved to candidate.stim")
    
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
