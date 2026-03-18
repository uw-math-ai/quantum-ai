import stim

baseline = """CX 5 0 0 5 5 0
H 0
CX 0 10 0 15 0 43
H 5 40 42
CX 5 0 40 0 42 0 10 1 1 10 10 1 5 1 40 1 42 1 15 2 2 15 15 2 5 2 40 2 42 2 25 3 3 25 25 3 3 20 3 43 5 3 20 4 4 20 20 4 5 4 43 6 6 43 43 6 6 30 6 35 8 6 39 6 43 6 44 6 30 7 7 30 30 7 8 7 39 7 43 7 44 7 35 8 8 35 35 8 35 8 39 8 43 8 44 8 43 9 9 43 43 9
H 9 40
CX 9 11 9 16 9 40
H 10 41
CX 10 9 41 9 11 10 10 11 11 10 11 10 41 10 16 11 11 16 16 11 16 11 41 11 16 12 12 16 16 12 12 21 12 26 21 13 13 21 21 13 26 14 14 26 26 14 40 15 15 40 40 15
S 15
H 15
S 15
CX 15 31 15 36
S 44
H 41 42 44
CX 30 15 35 15 39 15 41 15 42 15 43 15 44 15 31 16 16 31 31 16 30 16 35 16 39 16 41 16 42 16 43 16 44 16 36 17 17 36 36 17 30 17 35 17 39 17 41 17 42 17 43 17 44 17 30 18 18 30 30 18
H 18
CX 18 31 18 36 18 41
H 40 42
CX 40 18 42 18 31 19 19 31 31 19 40 19 42 19 36 20 20 36 36 20 40 20 42 20 40 21 21 40 40 21 21 22 21 27 27 23 23 27 27 23 41 24 24 41 41 24
S 24
H 24
S 24
CX 24 32 24 37
H 42
CX 39 24 42 24 43 24 44 24 32 25 25 32 32 25 39 25 42 25 43 25 44 25 37 26 26 37 37 26 39 26 42 26 43 26 44 26 35 27 27 35 35 27
H 27
CX 27 30 27 40 27 42
H 32
CX 32 27 40 28 28 40 40 28 32 28 30 29 29 30 30 29 32 29 32 30 30 32 32 30 30 35 30 40 35 31 31 35 35 31 40 32 32 40 40 32 42 33 33 42 42 33 33 38 33 42
H 44
CX 39 33 44 33 42 34 34 42 42 34 39 34 44 34 38 35 35 38 38 35 39 35 44 35 43 36 36 43 43 36
H 36
S 44
CX 36 37 36 38 36 44
H 43
CX 43 36 43 37 43 38 43 39 39 43 43 39 39 40 39 41 41 40 40 41 41 40 43 42 42 43 43 42 42 43 44 42 44 43
H 6 7 8 15 16 17 24 25 26
S 6 6 7 7 8 8 15 15 16 16 17 17 24 24 25 25 26 26
H 6 7 8 15 16 17 24 25 26
S 9 9 12 12 15 15 36 36 39 39 44 44"""

# Parse the circuit
circ = stim.Circuit(baseline)

# Expanded gates as triples
expanded = []
for inst in circ:
    targets = inst.targets_copy()
    if inst.name == "CX":
        for i in range(0, len(targets), 2):
            expanded.append(("CX", targets[i].value, targets[i+1].value))
    else:
        for t in targets:
            expanded.append((inst.name, t.value, None))

# Simplify: look for CX a b; CX a b pairs (with nothing in between on a or b)
# Iteratively simplify
def simplify(gates):
    changed = True
    while changed:
        changed = False
        i = 0
        while i < len(gates) - 1:
            # Check for CX a b; CX a b pattern
            g1 = gates[i]
            if g1[0] == "CX":
                a, b = g1[1], g1[2]
                # Look forward for matching CX
                for j in range(i+1, len(gates)):
                    g2 = gates[j]
                    if g2[0] == "CX" and g2[1] == a and g2[2] == b:
                        # Check if we can commute (no gates in between touch a or b)
                        can_commute = True
                        for k in range(i+1, j):
                            gk = gates[k]
                            if gk[0] == "CX":
                                if gk[1] in [a, b] or gk[2] in [a, b]:
                                    can_commute = False
                                    break
                            else:
                                if gk[1] in [a, b]:
                                    can_commute = False
                                    break
                        if can_commute:
                            # Remove both
                            gates.pop(j)
                            gates.pop(i)
                            changed = True
                            break
                    elif g2[0] == "CX" and (g2[1] in [a, b] or g2[2] in [a, b]):
                        break  # Can't commute past
                    elif g2[0] != "CX" and g2[1] in [a, b]:
                        break  # Can't commute past single qubit gate on a or b
            i += 1
    return gates

simplified = simplify(expanded.copy())
print(f"Original gates: {len(expanded)}")
print(f"Simplified gates: {len(simplified)}")

cx_count = sum(1 for g in simplified if g[0] == "CX")
print(f"CX count after simplification: {cx_count}")

# Reconstruct circuit
circ2 = stim.Circuit()
for g in simplified:
    if g[0] == "CX":
        circ2.append("CX", [g[1], g[2]])
    else:
        circ2.append(g[0], [g[1]])

print("\nSimplified circuit:")
print(circ2)
