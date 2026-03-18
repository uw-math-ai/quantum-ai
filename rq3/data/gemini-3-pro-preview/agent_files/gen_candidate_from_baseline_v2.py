import stim

# Read baseline
with open("baseline_candidate.stim", "r") as f:
    baseline_text = f.read()

baseline = stim.Circuit(baseline_text)

# Simulate to get tableau
sim = stim.TableauSimulator()
sim.do(baseline)
# Get the inverse tableau which maps |0> to current state
tableau = sim.current_inverse_tableau().inverse()

# Generate graph state circuit
circuit = tableau.to_circuit(method="graph_state")

# Replace RX with H and remove TICKS
c_str = str(circuit)
lines = c_str.split('\n')
new_lines = []
for line in lines:
    if line.startswith("RX "):
        new_lines.append(line.replace("RX ", "H "))
    elif line.startswith("TICK"):
        pass
    else:
        new_lines.append(line)

final_circuit_str = '\n'.join(new_lines)
with open("candidate_from_baseline_v2.stim", "w") as f:
    f.write(final_circuit_str)
print("Done")
