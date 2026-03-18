import stim

original_str = """H 0 1
CX 0 1 0 4
H 2 3
CX 1 2 1 3 1 4 1 5 1 8 1 14 2 4 2 5 2 6 2 9 2 10 4 3 3 4 4 3 3 6 3 10 4 5 4 7 4 8 4 11 4 14 5 6 5 7 5 9 5 11 5 12 6 7 6 12 6 13 7 13 11 8 12 8 13 8 14 8 9 10 12 9 13 9 14 9 12 10 13 10 14 10 12 11 11 12 12 11 11 12 13 11 14 11 13 12 14 12 14 13"""

c = stim.Circuit(original_str)
new_c = stim.Circuit()

# Parse instructions
instructions = []
for instr in c:
    instructions.append(instr)

# Add first 3
new_c.append(instructions[0])
new_c.append(instructions[1])
new_c.append(instructions[2])

# Add checks for qubits 1, 2, 3
# Check if they are in |+> state
# Use ancillas 15, 16, 17
# Circuit: H A; CX A Q; H A
# Measurement at end.

a1 = 15
a2 = 16
a3 = 17

new_c.append("H", [a1, a2, a3])
new_c.append("CX", [a1, 1, a2, 2, a3, 3])
new_c.append("H", [a1, a2, a3])

# Add the rest
for i in range(3, len(instructions)):
    new_c.append(instructions[i])

# Measure ancillas
new_c.append("M", [a1, a2, a3])

print(new_c)
