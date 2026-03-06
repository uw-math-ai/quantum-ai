import stim

stabilizers = [
    stim.PauliString("XXXXXX"),
    stim.PauliString("ZZZZZZ")
]

# We need 6 stabilizers to define a state. The problem only gives 2.
# This implies we are looking for ANY state that is stabilized by these two.
# Or maybe the user implies these are the ONLY generators and the rest can be arbitrary?
# "The final quantum state on the data qubits must be a +1 eigenstate of every provided stabilizer generator."
# This means we just need to satisfy these. We can pick the other 4 stabilizers to be anything convenient,
# as long as they commute with these two and each other.

# Let's try to find a full set of stabilizers.
# S1 = XXXXXX
# S2 = ZZZZZZ

# Let's pick simple ones like single Z's or pairs of Z's?
# Z0 Z1 ? Commutes with S2 (all Z).
# Does it commute with S1 (all X)?
# X0 X1 vs Z0 Z1 -> XZ=-YY, so anticommutes at 0 and 1. Two anticommutations -> Commutes.
# So Z0Z1 commutes with XXXXXX.

# Let's try adding Z0Z1, Z1Z2, Z2Z3, Z3Z4.
# These are 4 generators.
# S1, S2, Z0Z1, Z1Z2, Z2Z3, Z3Z4.
# Are they independent?
# S2 = Z0Z1 * Z1Z2 * Z2Z3 * Z3Z4 * Z4Z5 * Z5Z0? No.
# Z0Z1 * Z2Z3 * Z4Z5 = Z0Z1Z2Z3Z4Z5 = S2.
# So Z0Z1, Z2Z3, Z4Z5 are not independent if we include S2.

# Let's try to use stim's Tableau.from_stabilizers with allow_underconstrained=True
try:
    tableau = stim.Tableau.from_stabilizers(stabilizers, allow_underconstrained=True)
    circuit = tableau.to_circuit("elimination")
    print(circuit)
except Exception as e:
    print(e)
