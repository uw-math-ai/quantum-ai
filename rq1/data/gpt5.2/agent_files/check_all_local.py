import stim

# Load circuit
with open("circuit_54_graph_clean.stim", "r") as f:
    circuit_text = f.read()

circuit = stim.Circuit(circuit_text)

sim = stim.TableauSimulator()
sim.do_circuit(circuit)

# Failing stabilizer (index 15)
fail_stab = "IIIIIIIIIIIIIIIIIIIIIIIIIIIIIXIIXIIIIIIIIIIIIIIIIIIIII"

val = sim.peek_observable_expectation(stim.PauliString(fail_stab))
print(f"Expectation of failing stabilizer (index 15): {val}")

# Load all stabilizers
with open("stabilizers_54_v2.txt", "r") as f:
    stabilizers = [l.strip() for l in f if l.strip()]

print(f"Checking {len(stabilizers)} stabilizers...")
failed = []
for i, s in enumerate(stabilizers):
    val = sim.peek_observable_expectation(stim.PauliString(s))
    if val != 1:
        print(f"Stabilizer {i} failed locally: {val}")
        failed.append(i)

if not failed:
    print("All stabilizers passed locally.")
else:
    print(f"Locally failed: {failed}")
