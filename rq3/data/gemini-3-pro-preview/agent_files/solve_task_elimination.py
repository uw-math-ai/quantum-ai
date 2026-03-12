import stim
import sys

try:
    with open("baseline.stim") as f:
        baseline_circuit = stim.Circuit(f.read())
except Exception as e:
    print(f"Error loading baseline: {e}")
    sys.exit(1)

t_base = baseline_circuit.to_tableau()

print("Synthesizing elimination circuit from tableau...")
# method="elimination" produces a circuit with CX, H, S, etc.
# It is generally not 0-CX.
circuit_new = t_base.to_circuit(method="elimination")

# Check for resets
for instruction in circuit_new:
    if instruction.name in ["R", "RX", "RY"]:
        print(f"Warning: Found reset {instruction.name}")

# Save
with open("candidate_elimination.stim", "w") as f:
    f.write(str(circuit_new))

print("Candidate saved to candidate_elimination.stim")
cx = circuit_new.num_2_qubit_gates()
print(f"CX count: {cx}")
