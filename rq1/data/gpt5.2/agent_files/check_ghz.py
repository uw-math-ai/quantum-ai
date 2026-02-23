import stim

c = stim.Circuit("""
H 0
CX 0 1 1 2 2 3 3 4 4 5
""")

sim = stim.TableauSimulator()
sim.do(c)

# Current stabilizers
target_stabs = [
    stim.PauliString("XXXXXX"),
    stim.PauliString("ZZZZZZ")
]

print("Stabilizers check:")
for s in target_stabs:
    res = sim.peek_observable_expectation(s)
    print(f"{s}: {res}")
