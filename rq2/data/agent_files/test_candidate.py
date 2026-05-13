import stim
from analyze_circuit_v1 import analyze_circuit

# Construct the candidate circuit
# Original:
# CX 1 0 0 1 1 0
# H 0 2
# CX 0 2 0 3 0 4 0 6
# H 1
# CX 1 0 1 2 1 4 2 3 2 4 2 5 3 5 4 5 6 4 6 5

# Ancillas: 7, 8 (check 1), 9, 10 (check 2)
# Check 1: Z 0 2 4 6
# Check 2: Z 0 1 2 3

circuit_str = """
CX 1 0 0 1 1 0
H 0 2
CX 0 2 0 3 0 4 0 6

# Check 1: Z 0 2 4 6
H 8
CX 0 7 2 7 4 7 6 7
CX 8 7
H 8
M 7 8

# Check 2: Z 0 1 2 3
H 10
CX 0 9 1 9 2 9 3 9
CX 10 9
H 10
M 9 10

H 1
CX 1 0 1 2 1 4 2 3 2 4 2 5 3 5 4 5 6 4 6 5
"""

print("Checking candidate...")
analyze_circuit(circuit_str)
