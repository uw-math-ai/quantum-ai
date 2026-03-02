import stim

stabilizers_str = [
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

stabilizers = [stim.PauliString(s) for s in stabilizers_str]

try:
    # Try to create tableau from stabilizers.
    # Note: from_stabilizers creates a tableau T such that T(Z_k) = stabilizer[k].
    # If the list is shorter than N, we might need allow_underconstrained=True
    tableau = stim.Tableau.from_stabilizers(stabilizers, allow_underconstrained=True)
    
    # Generate circuit to implement this tableau
    # The circuit for T applied to |0...0> state prepares the state stabilized by {T(Z_k)} = {stabilizers[k]}.
    # The extra qubits (if underconstrained) will correspond to remaining Z_k which are mapped to something that commutes with the stabilizers.
    # This prepares *a* state in the code space.
    circuit = tableau.to_circuit()
    
    with open("data/gemini-3-pro-preview/agent_files/circuit_1.stim", "w") as f:
        f.write(str(circuit))
    print("Circuit written to data/gemini-3-pro-preview/agent_files/circuit_1.stim")
        
except Exception as e:
    print(f"Error creating tableau: {e}")
