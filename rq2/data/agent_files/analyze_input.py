import stim

circuit_str = """CX 1 0 0 1 1 0
H 0
CX 0 2 0 3 0 8
H 1
CX 1 0 2 1 1 2 2 1 2 1 3 2 2 3 3 2 3 2 3 4 3 5 7 6 6 7 7 6 6 7 8 6 8 7"""

print("Parsed circuit gates:")
c = stim.Circuit(circuit_str)
print(c)
