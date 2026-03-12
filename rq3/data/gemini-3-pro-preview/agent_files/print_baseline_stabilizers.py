import stim

sim = stim.TableauSimulator()
with open('current_task_baseline.stim', 'r') as f:
    c = stim.Circuit(f.read())
sim.do(c)
tab = sim.current_inverse_tableau().inverse()
print(f'First stabilizer (Z0): {tab.z_output(0)}')
print(f'First stabilizer (Z1): {tab.z_output(1)}')
