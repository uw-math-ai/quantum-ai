import stim
import sys

# Load baseline
try:
    with open("baseline.stim") as f:
        baseline_circuit = stim.Circuit(f.read())
except Exception as e:
    print(f"Error loading baseline: {e}")
    sys.exit(1)

print("Extracting tableau from baseline circuit...")
# The baseline circuit U maps |0> to |psi>.
# Its tableau T satisfies T(P) = U P U^dag.
# The stabilizers of |0> are Z_0, Z_1, ...
# The stabilizers of |psi> are U Z_i U^dag = T(Z_i).
# So the tableau T *is* the stabilizer tableau (if we interpret the columns appropriately).
# Stim's to_circuit(method="graph_state") works on a Tableau object.
# If we pass the tableau of the circuit, it should synthesize a circuit implementing the same unitary (up to Clifford phases?).
# Wait, method='graph_state' synthesizes a state preparation circuit for the state stabilized by the tableau's Z outputs?
# Documentation says: "Returns a circuit that prepares a state stabilized by the tableau's stabilizers."
# The "tableau's stabilizers" usually means the image of Z_i.
# So yes, T.to_circuit() should prepare the same state.

t_base = baseline_circuit.to_tableau()

# Extract stabilizers strings
stabilizers = []
for k in range(len(t_base)):
    stabilizers.append(t_base.z_output(k))

print(f"Extracted {len(stabilizers)} stabilizers from baseline.")

# Create new tableau from these stabilizers
# This ensures we get a canonical tableau for the state.
try:
    t_new = stim.Tableau.from_stabilizers(
        stabilizers,
        allow_redundant=True,
        allow_underconstrained=True
    )
    print("Created new tableau from extracted stabilizers.")
except Exception as e:
    print(f"Failed to create tableau from extracted stabilizers: {e}")
    sys.exit(1)

# Synthesize
print("Synthesizing graph state circuit from new tableau...")
circuit_new = t_new.to_circuit(method="graph_state")

# Replace RX with H
circuit_final = stim.Circuit()
for instruction in circuit_new:
    if instruction.name == "RX":
        circuit_final.append("H", instruction.targets_copy())
    else:
        circuit_final.append(instruction)

# Save
with open("candidate_graph_reconstructed.stim", "w") as f:
    f.write(str(circuit_final))

print("Candidate saved to candidate_graph_reconstructed.stim")
