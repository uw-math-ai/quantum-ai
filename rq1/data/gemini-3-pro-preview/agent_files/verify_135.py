import stim
import solve_135

stabilizers = solve_135.stabilizers

# Read circuit
with open("circuit_clean_135.stim", "r") as f:
    circuit_text = f.read()

try:
    circuit = stim.Circuit(circuit_text)
except Exception as e:
    print(f"Error parsing circuit: {e}")
    exit(1)

print("Verifying stabilizers...")
sim = stim.TableauSimulator()
sim.do(circuit)

all_good = True
for i, s_str in enumerate(stabilizers):
    s = stim.PauliString(s_str)
    # peek_observable_expectation returns 1 if stabilized by +S, -1 if by -S, 0 if not stabilized (random).
    val = sim.peek_observable_expectation(s)
    if val != 1:
        print(f"Stabilizer {i} failed: Expectation {val}")
        all_good = False
        # break

if all_good:
    print("All stabilizers preserved!")
else:
    print("Some stabilizers failed.")
