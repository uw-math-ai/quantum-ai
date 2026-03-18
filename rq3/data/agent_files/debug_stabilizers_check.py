import stim
import sys

# Extract stabilizers from optimize_session.py
with open("optimize_session.py") as f:
    content = f.read()
start = content.find("stabilizers = [")
end = content.find("]", start) + 1
exec(content[start:end]) # creates 'stabilizers' variable

# Load candidate
with open("candidate_final.stim") as f:
    circuit = stim.Circuit(f.read())

sim = stim.TableauSimulator()
sim.do(circuit)

failed_count = 0
for i, s_str in enumerate(stabilizers):
    s = stim.PauliString(s_str)
    ev = sim.peek_observable_expectation(s)
    if ev != 1:
        print(f"Failed {i}: {ev}")
        failed_count += 1

print(f"Total failed: {failed_count}")
