import stim

original_str = """H 0 1
CX 0 1 0 4
H 2 3
CX 1 2 1 3 1 4 1 5 1 8 1 14 2 4 2 5 2 6 2 9 2 10 4 3 3 4 4 3 3 6 3 10 4 5 4 7 4 8 4 11 4 14 5 6 5 7 5 9 5 11 5 12 6 7 6 12 6 13 7 13 11 8 12 8 13 8 14 8 9 10 12 9 13 9 14 9 12 10 13 10 14 10 12 11 11 12 12 11 11 12 13 11 14 11 13 12 14 12 14 13"""

c = stim.Circuit(original_str)
new_c = stim.Circuit()

instructions = list(c)

# Initial setup
new_c.append(instructions[0])
new_c.append(instructions[1])
new_c.append(instructions[2])

# Ancillas
# 15, 16, 17: X-checks on 1, 2, 3
# 18: Z_0 Z_4 check
# 19: X_0 X_4 check

# X-checks on 1, 2, 3
# H A, CX A Q, H A
new_c.append("H", [15, 16, 17])
new_c.append("CX", [15, 1, 16, 2, 17, 3])
new_c.append("H", [15, 16, 17])

# Z_0 Z_4 check (Ancilla 18)
# CX 0 18, CX 4 18
new_c.append("CX", [0, 18, 4, 18])

# X_0 X_4 check (Ancilla 19)
# H 19, CX 19 0, CX 19 4, H 19
new_c.append("H", [19])
new_c.append("CX", [19, 0, 19, 4])
new_c.append("H", [19])

# Rest of circuit
for i in range(3, len(instructions)):
    new_c.append(instructions[i])

# Measurements
new_c.append("M", [15, 16, 17, 18, 19])

print(new_c)
