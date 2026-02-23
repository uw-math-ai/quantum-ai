with open("stabilizers_72.txt", "r") as f:
    lines = [line.strip() for line in f if line.strip()]

print(f"Number of stabilizers: {len(lines)}")
for i, line in enumerate(lines):
    if len(line) != 72:
        print(f"Line {i} has length {len(line)}")
    else:
        pass # All good

import stim
try:
    s = stim.Tableau.from_stabilizers([stim.PauliString(l) for l in lines], allow_underconstrained=True)
    print(f"Tableau created with {len(s)} qubits")
except Exception as e:
    print(f"Error creating tableau: {e}")
