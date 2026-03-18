import stim
import itertools

baseline = '''CX 7 0 0 7 7 0
H 0
CX 0 21 0 28 0 45 0 46
H 7 42 43
CX 7 0 42 0 43 0 43 1 1 43 43 1
H 2 4 6
CX 1 2 1 4 1 6 1 28 7 1 42 1 28 2 2 28 28 2 2 45 2 46 35 2 42 2 14 3 3 14 14 3
H 3
CX 3 7 3 35 3 45 3 46 21 4 4 21 21 4 4 35 4 45 4 46 7 4 7 5 5 7 7 5 35 6 6 35 35 6 6 45 6 46 8 7 7 8 8 7
H 7
CX 7 22 7 29 7 45
H 43
CX 42 7 43 7 42 8 8 42 42 8
H 42
CX 8 21 8 29 8 42 8 45 8 46 8 48 43 8 29 9 9 29 29 9 9 45 36 9 15 10 10 15 15 10
H 10
CX 10 36 10 43 10 45 22 11 11 22 22 11 11 36 11 45 43 11 43 12 12 43 43 12 36 13 13 36 36 13 13 45 29 14 14 29 29 14
H 14
CX 14 23 14 30 14 46 28 14 28 15 15 28 28 15 15 30 46 16 16 46 46 16 16 30 31 16 33 16 38 16 40 16 47 16 48 16 46 17 17 46 46 17
H 17
CX 17 37 23 18 18 23 23 18 18 30 18 37 30 18 31 18 33 18 37 18 38 18 40 18 47 18 48 18 30 19 19 30 30 19 31 19 33 19 37 19 38 19 40 19 47 19 48 19 37 20 20 37 37 20 28 21 21 28 28 21
H 21
CX 21 24 21 31 21 47
H 29 44
CX 29 21 44 21 44 22 22 44 44 22 22 28 22 31 22 35 22 42 22 48 29 22 31 23 23 31 31 23 23 47 38 23 46 24 24 46 46 24
H 24
CX 24 29 24 38 24 47 46 25 25 46 46 25 25 38 25 47 29 25 29 26 26 29 29 26 38 27 27 38 38 27 27 47 44 28 28 44 44 28
H 28
CX 28 32 28 45 28 46 28 47 44 28 44 29 29 44 44 29 29 32 45 30 30 45 45 30 30 32 30 47 33 30 40 30 48 30
H 31
CX 31 39 32 39 32 46 33 32 39 32 40 32 46 32 48 32 39 33 33 39 39 33 33 46 39 33 40 33 48 33 46 34 34 46 46 34 43 35 35 43 43 35
H 35
CX 35 39 35 44 42 35 42 36 36 42 42 36 36 39 36 48 39 37 37 39 39 37 40 37 48 37 45 38 38 45 45 38
H 38
CX 38 40 38 48 44 39 39 44 44 39 39 40 48 39 48 40 40 48 48 40 48 41 41 48 48 41
H 42
CX 42 45 42 46 42 47 43 42 43 46 47 44 44 47 47 44 44 46 47 45 45 47 47 45
H 45
CX 45 48 46 47 46 48 47 46 48 46 48 47 47 48 48 47 47 48'''

circuit = stim.Circuit(baseline)
tab = circuit.to_tableau()

# Convert to ops
ops = []
for inst in circuit:
    if inst.name == 'CX':
        targets = inst.targets_copy()
        for i in range(0, len(targets), 2):
            ops.append(('CX', int(targets[i].value), int(targets[i+1].value)))
    elif inst.name == 'H':
        for t in inst.targets_copy():
            ops.append(('H', int(t.value)))

def ops_to_circuit_str(ops):
    lines = []
    i = 0
    while i < len(ops):
        if ops[i][0] == 'CX':
            cx_list = []
            while i < len(ops) and ops[i][0] == 'CX':
                cx_list.append(f'{ops[i][1]} {ops[i][2]}')
                i += 1
            lines.append('CX ' + ' '.join(cx_list))
        elif ops[i][0] == 'H':
            h_list = []
            while i < len(ops) and ops[i][0] == 'H':
                h_list.append(str(ops[i][1]))
                i += 1
            lines.append('H ' + ' '.join(h_list))
        else:
            lines.append(f'{ops[i][0]} {ops[i][1]}')
            i += 1
    return '\n'.join(lines)

# Look for same-pair CX gates that could be modified
# CX a b CX a b = I (if adjacent and nothing between)
# Find all positions of each CX pair
from collections import defaultdict
pair_pos = defaultdict(list)
for i, op in enumerate(ops):
    if op[0] == 'CX':
        pair_pos[(op[1], op[2])].append(i)

print("Looking for CX pair cancellations with commutation...")
# For each pair that appears twice, check if they can be moved adjacent
for (ctrl, tgt), positions in pair_pos.items():
    if len(positions) >= 2:
        for i in range(len(positions) - 1):
            p1, p2 = positions[i], positions[i+1]
            # Check what's between
            between = ops[p1+1:p2]
            
            # CX gates commute if they don't share qubits
            # OR if they share only the control (CX a b commutes with CX a c)
            # OR if they share only the target (CX a c commutes with CX b c)
            # But CX a b does NOT commute with CX b c (control of one = target of other)
            
            # Also, CX commutes through H on the control but not on the target
            # (conjugating CX by H on target gives CZ)
            
            can_commute = True
            for op in between:
                if op[0] == 'H':
                    if op[1] == tgt:  # H on target breaks commutation
                        can_commute = False
                        break
                    # H on control is OK
                elif op[0] == 'CX':
                    c2, t2 = op[1], op[2]
                    # Check commutation
                    if ctrl == t2 or tgt == c2:
                        can_commute = False
                        break
                    # ctrl == c2 or tgt == t2: commutes
                    # Different pairs: commutes
            
            if can_commute and between:
                # We can move CX at p2 to be adjacent to p1, then they cancel
                print(f"CX {ctrl} {tgt} at {p1} and {p2} can be moved adjacent (cancel!)")
                print(f"  Between: {between[:5]}..." if len(between) > 5 else f"  Between: {between}")

print("Done")
