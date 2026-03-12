import stim

stabilizers = [
    "XXIIXXIIIIIIIIIIIIIIIIIIIIII", "IIIIIIIXXIIXXIIIIIIIIIIIIIII", "IIIIIIIIIIIIIIXXIIXXIIIIIIII", "IIIIIIIIIIIIIIIIIIIIIXXIIXXI", 
    "XIXIXIXIIIIIIIIIIIIIIIIIIIII", "IIIIIIIXIXIXIXIIIIIIIIIIIIII", "IIIIIIIIIIIIIIXIXIXIXIIIIIII", "IIIIIIIIIIIIIIIIIIIIIXIXIXIX", 
    "IIIXXXXIIIIIIIIIIIIIIIIIIIII", "IIIIIIIIIIXXXXIIIIIIIIIIIIII", "IIIIIIIIIIIIIIIIIXXXXIIIIIII", "IIIIIIIIIIIIIIIIIIIIIIIIXXXX", 
    "ZZIIZZIIIIIIIIIIIIIIIIIIIIII", "IIIIIIIZZIIZZIIIIIIIIIIIIIII", "IIIIIIIIIIIIIIZZIIZZIIIIIIII", "IIIIIIIIIIIIIIIIIIIIIZZIIZZI", 
    "ZIZIZIZIIIIIIIIIIIIIIIIIIIII", "IIIIIIIZIZIZIZIIIIIIIIIIIIII", "IIIIIIIIIIIIIIZIZIZIZIIIIIII", "IIIIIIIIIIIIIIIIIIIIIZIZIZIZ", 
    "IIIZZZZIIIIIIIIIIIIIIIIIIIII", "IIIIIIIIIIZZZZIIIIIIIIIIIIII", "IIIIIIIIIIIIIIIIIZZZZIIIIIII", "IIIIIIIIIIIIIIIIIIIIIIIIZZZZ", 
    "XXXIIIIXXXIIIIXXXIIIIXXXIIII", "ZZZIIIIZZZIIIIZZZIIIIZZZIIII"
]

# Convert strings to PauliStrings
pauli_stabilizers = [stim.PauliString(s) for s in stabilizers]

# Create tableau from stabilizers
# allow_underconstrained=True is important if the stabilizers don't define a unique state (26 stabilizers for 28 qubits?)
# Let's check the length. 28 characters.
# 26 stabilizers for 28 qubits means there are 2 logical qubits (or 2 degrees of freedom).
# The baseline circuit operates on qubits up to 27 (0 to 27 is 28 qubits).
# If the state is not unique, any state satisfying the stabilizers is valid.
# Stim's from_stabilizers requires a full set if allow_underconstrained is False.
try:
    tableau = stim.Tableau.from_stabilizers(pauli_stabilizers, allow_underconstrained=True, allow_redundant=True)
except Exception as e:
    # Fallback: synthesize from baseline if provided stabilizers are inconsistent or problematic
    # But for now, let's assume they work or we need to fill the rest.
    print(f"Error creating tableau: {e}")
    exit(1)

# Synthesize circuit
# method="graph_state" is known to be efficient for CX count (uses CZs)
circuit = tableau.to_circuit(method="graph_state")

# Post-processing:
# The graph_state method might produce RX gates (reset + X).
# The instructions say "Do NOT introduce measurements, resets, or noise".
# If the circuit has RX, we should replace it with H if we assume input is |0>.
# RX targets are usually prepared in |+> state? No, RX implies reset to 0 then X?
# Actually Stim's RX is a reset-to-X-basis?
# Let's check what Stim produces.
# If it produces R (reset), we need to handle it.
# Ideally, we want a unitary that maps |00...0> to the state.
# Graph state circuits usually start with H on some qubits.
# If Stim uses "R" (Reset) gates, we should replace "R" with nothing (if we assume we start at 0) or simple gates.
# But "R" usually resets to 0. If we are already at 0, "R" is identity.
# However, "RX" resets to |+>. If we start at |0>, H takes us to |+>.
# So "RX" -> "H". "R" (or "RZ") -> Identity.

# Let's manually filter the circuit text to be safe, or just inspect it.
print(circuit)
