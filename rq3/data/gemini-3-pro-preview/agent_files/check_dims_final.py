import stim
with open("baseline_correct.stim", "r") as f:
    c = stim.Circuit(f.read())
print(f"Num qubits: {c.num_qubits}")
sim = stim.TableauSimulator()
sim.do(c)
t = sim.current_inverse_tableau().inverse()
print(f"Tableau len: {len(t)}")
