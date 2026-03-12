import stim

with open("baseline.stim", "r") as f:
    baseline = stim.Circuit(f.read())

print(f"Baseline num_qubits: {baseline.num_qubits}")
print(f"Max qubit index: {max(freq[0] for freq in baseline.count_determined_measurements().keys()) if baseline.count_determined_measurements() else 'N/A'}")
# better way to get max qubit
max_q = 0
for instr in baseline:
    for t in instr.targets_copy():
        if t.value > max_q:
            max_q = t.value
print(f"Max qubit index scan: {max_q}")

sim = stim.TableauSimulator()
sim.do(baseline)
print(f"Simulator num_qubits: {sim.num_qubits}")

tableau = sim.current_inverse_tableau().inverse()
print(f"Tableau len: {len(tableau)}")

candidate = tableau.to_circuit(method="graph_state")
print(f"Candidate num_qubits: {candidate.num_qubits}")
