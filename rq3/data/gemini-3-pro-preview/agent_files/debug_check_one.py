import stim

line = 'XXXXXXIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIII'
try:
    p = stim.PauliString(line)
    print(f'Parsed PauliString: {p}')
except Exception as e:
    print(f'Parsing error: {e}')

sim = stim.TableauSimulator()
with open('current_task_baseline.stim', 'r') as f:
    c = stim.Circuit(f.read())
sim.do(c)

exp = sim.peek_observable_expectation(p)
print(f'Expectation: {exp}')

# Also check directly against z_output(0)
z0 = sim.current_inverse_tableau().inverse().z_output(0)
print(f'Z0 output: {z0}')

# Check equality
print(f'Equal? {p == z0}')
