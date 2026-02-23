import stim

c = stim.Circuit()
c.append("H", [0])
c.append("CX", [0, 1])
c.append("CX", [1, 2])
c.append("CX", [2, 3])
c.append("CX", [3, 4])
c.append("CX", [4, 5])

print("Circuit:")
print(c)

sim = stim.TableauSimulator()
sim.do(c)

# Check XXXXXX
t1 = stim.PauliString("XXXXXX")
exp1 = sim.peek_observable_expectation(t1)
print(f"Expectation XXXXXX: {exp1}")

# Check ZZZZZZ
t2 = stim.PauliString("ZZZZZZ")
exp2 = sim.peek_observable_expectation(t2)
print(f"Expectation ZZZZZZ: {exp2}")
