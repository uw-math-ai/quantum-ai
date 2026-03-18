import stim

# Based on the analysis, let's build an optimized circuit

# Single qubit operations after simplification (removing HH pairs):
# Q0: S (H H S -> S)
# Q1: H X H -> Z (since HXH = Z)
# Q2: H Z -> becomes H then Z at end
# Q3: H Z S 
# Q4: empty (H H)
# Q5: H S
# Q6: H S
# Q7: H X H S -> Z S (HXH = Z)
# Q8: H X H -> Z
# Q9: H Z H -> X (HZH = X)
# Q10: H X S
# Q11: H Y
# Q12: H Y S
# Q13: H Z S
# Q14: H Z H S -> X S (HZH = X)
# Q15: H Y H -> (HYH = -Y, but Y = iXZ, so HYH = H*iXZ*H = iZ*X = -iXZ = -Y)
#      For Clifford purposes: HYH = -Y = Y (up to sign)
# Q16: empty (H H)
# Q17: H Z S
# Q18: H Z
# Q19: H S
# Q20: H X S
# Q21: H
# Q22: H
# Q23: H
# Q24: empty (H H)
# Q25: H Z H -> X
# Q26: H Z H -> X
# Q27: H Z H -> X
# Q28: H
# Q29: H X
# Q30: H X
# Q31: empty (H H)
# Q32: H Z H -> X
# Q33: empty (H H)
# Q34: empty (H H)
# Q35: H
# Q36: H
# Q37: H
# Q38: empty (H H)
# Q39: H Z H -> X
# Q40: H Z H -> X
# Q41: H Z H -> X
# Q42: H X
# Q43: H
# Q44: H
# Q45: H Z H -> X
# Q46: empty (H H)
# Q47: H Z H -> X
# Q48: H Z H -> X

# The structure is:
# 1. First H layer on qubits that end up needing H (considering cancellations)
# 2. CZ gates
# 3. Final single-qubit corrections

# Key insight: H...H at beginning and end can cancel
# For qubits where the pattern is H CZ... H, the H's stay
# For qubits where pattern is H CZ... (no final H), we need H at start

# Let me trace through more carefully
# Original: H(all) -> CZ -> X/Y/Z/S -> H(some) -> S(some)

# The final gates after CZ are:
# X 1 7 8 10 20 29 30 42
# Y 11 12 15
# Z 2 3 9 13 14 17 18 25 26 27 32 39 40 41 45 47 48
# S 3 5 6 10 12 13 17 19 20
# H 0 1 4 7 8 9 14 15 16 24 25 26 27 31 32 33 34 38 39 40 41 45 46 47 48
# S 0 7 14

# So the full sequence per qubit after CZ:
# Q0: H -> S
# Q1: X -> H 
# Q2: Z
# Q3: Z -> S
# Q4: H
# Q5: S
# Q6: S
# Q7: X -> H -> S
# Q8: X -> H
# Q9: Z -> H
# Q10: X -> S
# Q11: Y
# Q12: Y -> S
# Q13: Z -> S
# Q14: Z -> H -> S
# Q15: Y -> H
# Q16: H
# Q17: Z -> S
# Q18: Z
# Q19: S
# Q20: X -> S
# Q21: (none)
# Q22: (none)
# Q23: (none)
# Q24: H
# Q25: Z -> H
# Q26: Z -> H
# Q27: Z -> H
# Q28: (none)
# Q29: X
# Q30: X
# Q31: H
# Q32: Z -> H
# Q33: H
# Q34: H
# Q35: (none)
# Q36: (none)
# Q37: (none)
# Q38: H
# Q39: Z -> H
# Q40: Z -> H
# Q41: Z -> H
# Q42: X
# Q43: (none)
# Q44: (none)
# Q45: Z -> H
# Q46: H
# Q47: Z -> H
# Q48: Z -> H

# Now when we compose with the initial H:
# Q0: H -> (CZ) -> H -> S = H CZ H S. Since HH = I after CZ corrections... 
# Actually, the CZ layer is in between, so we can't just cancel H's

# Let me think differently. The circuit is:
# H(all 49) -> CZ(153 gates) -> corrections
# Where corrections = X/Y/Z/S/H/S as specified

# To optimize, I need to understand: what's the minimal single-qubit layer after CZ?

# Let's compute the effective single-qubit gate per qubit (composing all gates after CZ)
# Then see if we can reduce the total gate count

def compose_gates(gates):
    """Compose a list of single-qubit Clifford gates into a minimal form."""
    # Clifford group on 1 qubit has 24 elements
    # Use matrix representation mod 2 for X, Z behavior
    # [x_in -> x_out, x_in -> z_out]
    # [z_in -> x_out, z_in -> z_out]
    
    # For state prep from |0>, we only care about Z stabilizer becoming some Pauli
    # Start with Z stabilizer, track what it becomes
    
    # Actually for simplicity, let's just compose as strings
    result = list(gates)
    
    # Simplification rules
    changed = True
    while changed:
        changed = False
        new_result = []
        i = 0
        while i < len(result):
            if i + 1 < len(result):
                pair = (result[i], result[i+1])
                # Identity cancellations
                if pair in [('H', 'H'), ('X', 'X'), ('Y', 'Y'), ('Z', 'Z')]:
                    i += 2
                    changed = True
                    continue
                # SS = Z
                if pair == ('S', 'S'):
                    new_result.append('Z')
                    i += 2
                    changed = True
                    continue
                # SZ = ZS (commute)
                if pair == ('S', 'Z'):
                    new_result.append('Z')
                    new_result.append('S')
                    i += 2
                    changed = True
                    continue
                # XZ = ZX (anticommute but XZ = -ZX = iY... complicated)
                # Actually XZ = -ZX and XZ = iY (not Y!)
                # For Clifford: XZ|psi> = -ZX|psi>, so the effect is same up to phase
                # For stabilizer prep, phase matters for sign of stabilizer
                
                # HZH = X
                if i + 2 < len(result) and (result[i], result[i+1], result[i+2]) == ('H', 'Z', 'H'):
                    new_result.append('X')
                    i += 3
                    changed = True
                    continue
                # HXH = Z
                if i + 2 < len(result) and (result[i], result[i+1], result[i+2]) == ('H', 'X', 'H'):
                    new_result.append('Z')
                    i += 3
                    changed = True
                    continue
                # HSH = S_DAG (not directly useful)
            new_result.append(result[i])
            i += 1
        result = new_result
    
    return result

# The post-CZ corrections
post_cz = {
    0: ['H', 'S'],
    1: ['X', 'H'],
    2: ['Z'],
    3: ['Z', 'S'],
    4: ['H'],
    5: ['S'],
    6: ['S'],
    7: ['X', 'H', 'S'],
    8: ['X', 'H'],
    9: ['Z', 'H'],
    10: ['X', 'S'],
    11: ['Y'],
    12: ['Y', 'S'],
    13: ['Z', 'S'],
    14: ['Z', 'H', 'S'],
    15: ['Y', 'H'],
    16: ['H'],
    17: ['Z', 'S'],
    18: ['Z'],
    19: ['S'],
    20: ['X', 'S'],
    21: [],
    22: [],
    23: [],
    24: ['H'],
    25: ['Z', 'H'],
    26: ['Z', 'H'],
    27: ['Z', 'H'],
    28: [],
    29: ['X'],
    30: ['X'],
    31: ['H'],
    32: ['Z', 'H'],
    33: ['H'],
    34: ['H'],
    35: [],
    36: [],
    37: [],
    38: ['H'],
    39: ['Z', 'H'],
    40: ['Z', 'H'],
    41: ['Z', 'H'],
    42: ['X'],
    43: [],
    44: [],
    45: ['Z', 'H'],
    46: ['H'],
    47: ['Z', 'H'],
    48: ['Z', 'H'],
}

# Now, considering the initial H on all qubits:
# The full sequence for qubit q is: H -> CZ -> post_cz[q]
# At the end, some qubits get another H

# Can we simplify the initial H and post-CZ H?
# No, because the CZ layer is in between.

# BUT: we can simplify by changing CZ to operate on different basis
# CZ operates on X basis (applies Z when control is |+>)
# If we flip basis before/after CZ, we get CX behavior

# Actually the simplest optimization: keep the structure, minimize post-CZ gates
# Current: 49 H + 153 CZ + ~114 post-CZ gates = ~316 volume
# Can we reduce?

# Let's check if some post-CZ gates can be moved before CZ
# CZ commutes with Z gates on either qubit: CZ * (Z_a) = (Z_a) * CZ
# CZ commutes with H on other qubits

# So we can move Z gates from after CZ to before CZ (phase doesn't matter for state prep)
# This doesn't reduce count, but might enable further simplifications

# Let's compute the total gate count
total_post = sum(len(v) for v in post_cz.values())
print(f"Post-CZ gates: {total_post}")
print(f"Total gates: 49 H + 153 CZ + {total_post} = {49 + 153 + total_post}")

# The validated working circuit
best_circuit = """H 0 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 18 19 20 21 22 23 24 25 26 27 28 29 30 31 32 33 34 35 36 37 38 39 40 41 42 43 44 45 46 47 48
CZ 0 3 0 5 0 6 1 2 1 5 1 6 2 4 2 25 2 26 2 27 2 39 2 40 2 41 2 46 2 47 2 48 3 4 3 5 3 6 3 25 3 26 3 27 3 39 3 40 3 41 3 46 3 47 3 48 4 5 5 6 6 25 6 26 6 27 6 39 6 40 6 41 6 46 6 47 6 48 7 10 7 12 7 13 8 10 8 11 8 13 9 10 9 11 9 12 10 12 10 13 11 25 11 26 11 27 11 32 11 33 11 34 11 46 11 47 11 48 12 13 12 25 12 26 12 27 12 32 12 33 12 34 12 46 12 47 12 48 13 25 13 26 13 27 13 32 13 33 13 34 13 46 13 47 13 48 14 17 14 19 14 20 15 17 15 18 15 20 16 17 16 18 16 19 17 19 17 20 18 25 18 26 18 27 18 32 18 33 18 34 18 39 18 40 18 41 19 20 19 25 19 26 19 27 19 32 19 33 19 34 19 39 19 40 19 41 20 25 20 26 20 27 20 32 20 33 20 34 20 39 20 40 20 41 21 24 21 26 21 27 22 24 22 25 22 27 23 24 23 25 23 26 28 31 28 33 28 34 29 31 29 32 29 34 30 31 30 32 30 33 35 38 35 40 35 41 36 38 36 39 36 41 37 38 37 39 37 40 42 45 42 47 42 48 43 45 43 46 43 48 44 45 44 46 44 47
X 1 7 8 10 20 29 30 42
Y 11 12 15
Z 2 3 9 13 14 17 18 25 26 27 32 39 40 41 45 47 48
S 3 5 6 10 12 13 17 19 20
H 0 1 4 7 8 9 14 15 16 24 25 26 27 31 32 33 34 38 39 40 41 45 46 47 48
S 0 7 14"""

# Volume calculation using single-qubit gates as 1, CZ as 1 per pair
def count_volume(circuit_str):
    vol = 0
    lines = circuit_str.strip().split('\n')
    for line in lines:
        parts = line.split()
        gate = parts[0]
        if gate in ['CZ', 'CX']:
            vol += (len(parts) - 1) // 2
        else:
            vol += len(parts) - 1
    return vol

print(f"Volume of best circuit: {count_volume(best_circuit)}")

with open('data/claude-opus-4.6/agent_files/best_v2.stim', 'w') as f:
    f.write(best_circuit)
