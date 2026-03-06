import stim

with open("data/gemini-3-pro-preview/agent_files/stabilizers_171.txt", "r") as f:
    stabilizers = [l.strip() for l in f if l.strip()]

t = stim.Tableau.from_stabilizers([stim.PauliString(s) for s in stabilizers], allow_underconstrained=True)
print("Tableau created")
# Check signs
# The signs of the generators in the tableau should be +1?
# No, from_stabilizers creates a state stabilized by the given stabilizers.
# If I use allow_underconstrained, it fills the rest.
# But the provided ones should be stabilized with +1.

# Let's check expectations on the Tableau itself.
# But I don't have the tableau object in the tool.
# I have the circuit.

c = t.to_circuit()
sim = stim.TableauSimulator()
sim.do_circuit(c)

failed = []
for i, s_str in enumerate(stabilizers):
    s = stim.PauliString(s_str)
    if sim.peek_observable_expectation(s) != 1:
        failed.append(i)

print(f"Failed indices locally: {failed}")
