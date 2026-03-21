
import stim

with open('baseline.stim', 'r') as f:
    circuit = stim.Circuit(f.read())

print("Original first 5:")
for i, inst in enumerate(circuit):
    if i < 5:
        print(inst)
    else:
        break
