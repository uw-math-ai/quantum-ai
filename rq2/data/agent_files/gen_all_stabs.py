import stim

circuit = stim.Circuit.from_file('input.stim')
sim = stim.TableauSimulator()
sim.do(circuit)

tableau = sim.current_inverse_tableau().inverse()

with open('all_stabilizers.txt', 'w') as f:
    for k in range(135):
        s = tableau.z_output(k)
        f.write(str(s) + '\n')

print("Generated all_stabilizers.txt with 135 stabilizers.")
