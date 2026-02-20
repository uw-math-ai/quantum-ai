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

try:
    # Convert string stabilizers to stim.PauliString objects
    pauli_stabilizers = [stim.PauliString(s) for s in stabilizers]
    
    # Create a Tableau from the stabilizers
    # allow_underconstrained=True is important because we have 26 stabilizers for 28 qubits
    tableau = stim.Tableau.from_stabilizers(pauli_stabilizers, allow_underconstrained=True)
    
    print(f"Tableau num_qubits: {len(tableau)}")

    # Convert to a circuit that prepares this state
    circuit = tableau.to_circuit("elimination")
    
    with open("data/gemini-3-pro-preview/agent_files/circuit_28_gen.stim", "w") as f:
        for instruction in circuit:
            f.write(str(instruction) + "\n")
            
    print("Circuit saved to data/gemini-3-pro-preview/agent_files/circuit_28_gen.stim")
    
except Exception as e:
    print(f"Error: {e}")
