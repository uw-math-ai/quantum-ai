import sys

filename = "circuit_anpaz_v1.stim"
qubit = 61

print(f"Tracking qubit {qubit}")
with open(filename, "r") as f:
    lines = f.readlines()

for i, line in enumerate(lines):
    line = line.strip()
    if not line: continue
    parts = line.split()
    gate = parts[0]
    try:
        targets = [int(x) for x in parts[1:]]
    except ValueError:
        continue # skip invalid
    
    if gate == "H":
        if qubit in targets:
            print(f"Line {i+1}: H on {qubit}")
    elif gate == "S":
        if qubit in targets:
            print(f"Line {i+1}: S on {qubit}")
    elif gate == "CX":
        # Pairs
        for j in range(0, len(targets), 2):
            if j+1 >= len(targets): break
            c = targets[j]
            t = targets[j+1]
            if c == qubit:
                print(f"Line {i+1}: CX {c} -> {t} (Control)")
            if t == qubit:
                print(f"Line {i+1}: CX {c} -> {t} (Target)")
