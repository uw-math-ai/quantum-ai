
import stim

with open('baseline.stim', 'r') as f:
    circuit = stim.Circuit(f.read())

for i, inst in enumerate(circuit):
    if i < 10:
        print(f"{i}: {inst.name} {inst}")
