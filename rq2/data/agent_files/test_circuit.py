import stim

circuit_str = """H 0
CX 0 1 0 2 0 3 0 4 0 5 2 1 3 1 4 1 5 1
R 6 7 8 9
H 6 9
CX 6 7
CZ 0 6 1 6 2 6 3 6 4 6 5 6
CX 6 7
CX 9 8
CX 0 8 1 8 2 8 3 8 4 8 5 8
CX 9 8
H 6 9
M 6 7 8 9
"""

try:
    c = stim.Circuit(circuit_str)
    print("Valid circuit")
    print(c)
except Exception as e:
    print(f"Invalid circuit: {e}")
