import stim

with open("target_stabilizers.txt", "r") as f:
    stabs = [line.strip() for line in f if line.strip()]

s68 = stim.PauliString(stabs[68])
s118 = stim.PauliString(stabs[118])

print(f"S68:  {s68}")
print(f"S118: {s118}")
print(f"Commutes: {s68.commutes(s118)}")

# Check baseline behavior on these two
with open("baseline.stim", "r") as f:
    base_circ = stim.Circuit(f.read())

sim = stim.TableauSimulator()
sim.do(base_circ)

print(f"Base Exp S68: {sim.peek_observable_expectation(s68)}")
print(f"Base Exp S118: {sim.peek_observable_expectation(s118)}")
