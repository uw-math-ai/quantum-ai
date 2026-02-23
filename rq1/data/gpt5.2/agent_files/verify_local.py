import stim
from solve_119 import stabilizers

circuit_str = open("circuit_119.stim").read()
circuit = stim.Circuit(circuit_str)
sim = stim.TableauSimulator()
sim.do(circuit)

# Check each stabilizer
failed = []
for i, s in enumerate(stabilizers):
    p = stim.PauliString(s)
    # expectation value: +1 or -1
    # measure_expectation returns +1 or -1
    val = sim.peek_observable_expectation(p)
    if val != 1:
        print(f"Failed stabilizer {i}: {val}")
        failed.append(i)

print(f"Total failed: {len(failed)}")
