import stim

# Define stabilizers for 15 qubits - This looks like a 15-qubit Reed-Muller code
# The X stabilizers and Z stabilizers have the same pattern
# This is the [[15,7,3]] quantum Hamming code

stabilizers = [
    "IIIIIIIXXXXXXXX",  # X on 7-14
    "IIIXXXXIIIIXXXX",  # X on 3-6, 11-14
    "IXXIIXXIIXXIIXX",  # X on 1-2, 5-6, 9-10, 13-14
    "XIXIXIXIXIXIXIX",  # X on 0, 2, 4, 6, 8, 10, 12, 14
    "IIIIIIIZZZZZZZZ",  # Z on 7-14
    "IIIZZZZIIIIZZZZ",  # Z on 3-6, 11-14
    "IZZIIZZIIZZIIZZ",  # Z on 1-2, 5-6, 9-10, 13-14
    "ZIZIZIZIZIZIZIZ",  # Z on 0, 2, 4, 6, 8, 10, 12, 14
]

# This is a CSS code - X and Z stabilizers have identical support patterns
# Each stabilizer has support on qubits where the corresponding bit in the binary representation is 1

# For index i (0..14), qubit i is in stabilizer j if bit j of i is 1
# Stabilizer 0 (X on 7-14): qubits with bit 3 set (8,9,10,11,12,13,14) - wait that's bits 3,2,1,0
# Let me recalculate...

# Looking at the pattern:
# S0: IIIIIIIXXXXXXXX - qubits 7,8,9,10,11,12,13,14 - where i >= 8 or bit 3 is set (for i in 0..14)
# Actually qubits 7-14 means indices 7,8,9,10,11,12,13,14

# Let me think about this differently - this is a [[15,7,3]] Hamming code
# The qubits correspond to nonzero elements of GF(2^4)
# But we have 15 qubits numbered 0-14

# Let's try a direct construction approach
# For CSS codes, we can prepare using:
# 1. Prepare |0...0>
# 2. Apply H to data qubits in the code
# 3. Apply CZ/CX based on stabilizer structure

# Let's try constructing a circuit manually based on the structure
# The X stabilizers define which qubits need H gates
# The Z stabilizers define entanglement pattern

# Simple approach: encode using the stabilizer structure
# For a CSS code, we can use encoding circuit based on generator matrix

# Let me try a different synthesis approach - using CX gates directly
print("Testing manual circuit construction...")

# The stabilizers have a very regular pattern - they're based on binary representation
# Qubit i is in X-stab j if bit (j) of (i+1) is 1
# Let's verify:
for j in range(4):
    print(f"X-stab {j}: ", end="")
    for i in range(15):
        if ((i+1) >> (3-j)) & 1:
            print("X", end="")
        else:
            print("I", end="")
    print()

print("\nExpected:")
for s in stabilizers[:4]:
    print(s)

# Based on this structure, we can construct a simpler circuit
# The [[15,7,3]] Hamming code has 7 logical qubits and 4 stabilizer generators (each for X and Z)

# Let's try the elimination circuit which already works
circuit = stim.Circuit("""
CX 7 0 0 7 7 0
H 3
CX 3 0 4 0 5 0 6 0 8 0 10 0 12 0 13 0 2 1 1 2 2 1
H 1
CX 1 3 1 6 1 9 1 12 1 13 3 2 2 3 3 2 2 6 2 8 2 10 2 12 2 14
H 3
CX 3 5 3 8 3 11 3 12 3 13 3 14 5 4 4 5 5 4 6 4 9 4 10 4 11 4 12 4 6 5 5 6 6 5 8 5 9 5 10 5 13 5 14 5 8 6 6 8 8 6
H 7
CX 7 8 7 9 7 10 7 11 7 12 7 13 7 14 9 8 10 8 11 8 12 8 13 8 14 8
""")

# Count gates
cx_count = sum(1 for inst in circuit if inst.name == 'CX')
h_count = sum(1 for inst in circuit if inst.name == 'H')
print(f"\nElimination circuit: CX={cx_count}, H={h_count}")

# Let me try a more direct approach - synthesize from the stabilizer structure
# Since this is a CSS code with transversal structure, there's a simple encoding

# For the [[15,7,3]] Hamming code:
# - 15 physical qubits
# - 7 logical qubits (qubits 0,1,2,4,8... at Hamming positions)
# - 4 X stabilizers, 4 Z stabilizers

# Standard encoding for CSS codes:
# Start with |0...0>
# For each X stabilizer, apply H to one qubit and CX to others in that stabilizer

# Let me try a simpler encoding
print("\nTrying simplified encoding...")

# For a standard form CSS code encoding:
# 1. Initialize in |0>^n
# 2. For each X-stabilizer, pick an anchor qubit, apply H, then CX from anchor to other qubits in stabilizer

# The X stabilizers:
# X0: qubits 7-14 (8 qubits)
# X1: qubits 3,4,5,6,11,12,13,14 (8 qubits)
# X2: qubits 1,2,5,6,9,10,13,14 (8 qubits)
# X3: qubits 0,2,4,6,8,10,12,14 (8 qubits)

# Try a cascade encoding
simple_circuit = stim.Circuit("""
H 14
CX 14 7 14 8 14 9 14 10 14 11 14 12 14 13
H 11
CX 11 3 11 4 11 5 11 6
H 9
CX 9 1 9 2 9 5 9 6
H 8
CX 8 0 8 2 8 4 8 6
""")

print(f"Simple circuit:\n{simple_circuit}")

# Test this circuit
pauli_strings = [stim.PauliString(s) for s in stabilizers]
tableau = stim.Tableau.from_stabilizers(pauli_strings, allow_underconstrained=True)
sim = stim.TableauSimulator()
sim.do_circuit(simple_circuit)

# Check each stabilizer
print("\nChecking stabilizers with simple circuit:")
for i, s in enumerate(stabilizers):
    ps = stim.PauliString(s)
    exp = sim.peek_observable_expectation(ps)
    print(f"  S{i}: {s} -> {exp}")
