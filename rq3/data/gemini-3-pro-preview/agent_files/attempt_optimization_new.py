import stim
import sys

# Target stabilizers
stabilizers_str = [
    "XXIIXXIIIIIIIIIIIIIIIIIIIIII", "IIIIIIIXXIIXXIIIIIIIIIIIIIII", "IIIIIIIIIIIIIIXXIIXXIIIIIIII", "IIIIIIIIIIIIIIIIIIIIIXXIIXXI", 
    "XIXIXIXIIIIIIIIIIIIIIIIIIIII", "IIIIIIIXIXIXIXIIIIIIIIIIIIII", "IIIIIIIIIIIIIIXIXIXIXIIIIIII", "IIIIIIIIIIIIIIIIIIIIIXIXIXIX", 
    "IIIXXXXIIIIIIIIIIIIIIIIIIIII", "IIIIIIIIIIXXXXIIIIIIIIIIIIII", "IIIIIIIIIIIIIIIIIXXXXIIIIIII", "IIIIIIIIIIIIIIIIIIIIIIIIXXXX", 
    "ZZIIZZIIIIIIIIIIIIIIIIIIIIII", "IIIIIIIZZIIZZIIIIIIIIIIIIIII", "IIIIIIIIIIIIIIZZIIZZIIIIIIII", "IIIIIIIIIIIIIIIIIIIIIZZIIZZI", 
    "ZIZIZIZIIIIIIIIIIIIIIIIIIIII", "IIIIIIIZIZIZIZIIIIIIIIIIIIII", "IIIIIIIIIIIIIIZIZIZIZIIIIIII", "IIIIIIIIIIIIIIIIIIIIIZIZIZIZ", 
    "IIIZZZZIIIIIIIIIIIIIIIIIIIII", "IIIIIIIIIIZZZZIIIIIIIIIIIIII", "IIIIIIIIIIIIIIIIIZZZZIIIIIII", "IIIIIIIIIIIIIIIIIIIIIIIIZZZZ", 
    "XXXIIIIXXXIIIIXXXIIIIXXXIIII", "ZZZIIIIZZZIIIIZZZIIIIZZZIIII"
]

pauli_stabilizers = []
for s in stabilizers_str:
    pauli_stabilizers.append(stim.PauliString(s))

# Create tableau
try:
    # Use allow_underconstrained=True to fill degrees of freedom
    # Use allow_redundant=True just in case
    tableau = stim.Tableau.from_stabilizers(pauli_stabilizers, allow_underconstrained=True, allow_redundant=True)
except Exception as e:
    sys.stderr.write(f"Error creating tableau: {e}\n")
    sys.exit(1)

# Generate circuit using graph state method
try:
    circuit = tableau.to_circuit(method="graph_state")
except Exception as e:
    sys.stderr.write(f"Error generating circuit: {e}\n")
    sys.exit(1)

# Post-process the circuit
new_circuit = stim.Circuit()
for instruction in circuit:
    if instruction.name == "RX":
        # RX resets to |+>. If input is |0>, H does the same.
        targets = instruction.targets_copy()
        new_circuit.append("H", targets)
    elif instruction.name == "R" or instruction.name == "RZ":
        # R resets to |0>. If input is |0>, this is identity.
        pass
    elif instruction.name in ["M", "MX", "MY", "MZ", "MPP"]:
        sys.stderr.write(f"Error: Circuit contains measurement {instruction}\n")
        sys.exit(1)
    else:
        new_circuit.append(instruction)

# Verify stabilizers
sim = stim.TableauSimulator()
sim.do(new_circuit)
for i, stab in enumerate(pauli_stabilizers):
    expectation = sim.peek_observable_expectation(stab)
    if expectation != 1:
        sys.stderr.write(f"Stabilizer {i} not preserved! Expectation: {expectation}\n")

print(new_circuit)
