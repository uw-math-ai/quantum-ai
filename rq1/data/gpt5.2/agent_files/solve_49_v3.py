import stim
import numpy as np

# All stabilizers
stabilizers_raw = [
    "XXIIXXIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIII",   # 0
    "IIIIIIIXXIIXXIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIII",   # 1
    "IIIIIIIIIIIIIIXXIIXXIIIIIIIIIIIIIIIIIIIIIIIIIIIII",   # 2
    "IIIIIIIIIIIIIIIIIIIIIXXIIXXIIIIIIIIIIIIIIIIIIIIII",   # 3
    "IIIIIIIIIIIIIIIIIIIIIIIIIIIIXXIIXXIIIIIIIIIIIIIII",   # 4
    "IIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIXXIIXXIIIIIIII",   # 5
    "IIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIXXIIXXI",   # 6
    "XIXIXIXIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIII",   # 7
    "IIIIIIIXIXIXIXIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIII",   # 8
    "IIIIIIIIIIIIIIXIXIXIXIIIIIIIIIIIIIIIIIIIIIIIIIIII",   # 9
    "IIIIIIIIIIIIIIIIIIIIIXIXIXIXIIIIIIIIIIIIIIIIIIIII",   # 10
    "IIIIIIIIIIIIIIIIIIIIIIIIIIIIXIXIXIXIIIIIIIIIIIIII",   # 11
    "IIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIXIXIXIXIIIIIII",   # 12
    "IIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIXIXIXIX",   # 13
    "IIIXXXXIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIII",   # 14
    "IIIIIIIIIIXXXXIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIII",   # 15
    "IIIIIIIIIIIIIIIIIXXXXIIIIIIIIIIIIIIIIIIIIIIIIIIII",   # 16
    "IIIIIIIIIIIIIIIIIIIIIIIIXXXXIIIIIIIIIIIIIIIIIIIII",   # 17
    "IIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIXXXXIIIIIIIIIIIIII",   # 18
    "IIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIXXXXIIIIIII",   # 19
    "IIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIXXXX",   # 20
    "ZZIIZZIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIII",   # 21
    "IIIIIIIZZIIZZIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIII",   # 22
    "IIIIIIIIIIIIIIZZIIZZIIIIIIIIIIIIIIIIIIIIIIIIIIIII",   # 23
    "IIIIIIIIIIIIIIIIIIIIIZZIIZZIIIIIIIIIIIIIIIIIIIIII",   # 24
    "IIIIIIIIIIIIIIIIIIIIIIIIIIIIZZIIZZIIIIIIIIIIIIIII",   # 25
    "IIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIZZIIZZIIIIIIII",   # 26
    "IIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIZZIIZZI",   # 27
    "ZIZIZIZIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIII",   # 28
    "IIIIIIIZIZIZIZIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIII",   # 29
    "IIIIIIIIIIIIIIZIZIZIZIIIIIIIIIIIIIIIIIIIIIIIIIIII",   # 30
    "IIIIIIIIIIIIIIIIIIIIIZIZIZIZIIIIIIIIIIIIIIIIIIIII",   # 31
    "IIIIIIIIIIIIIIIIIIIIIIIIIIIIZIZIZIZIIIIIIIIIIIIII",   # 32
    "IIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIZIZIZIZIIIIIII",   # 33
    "IIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIZIZIZIZ",   # 34
    "IIIZZZZIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIII",   # 35
    "IIIIIIIIIIZZZZIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIII",   # 36
    "IIIIIIIIIIIIIIIIIZZZZIIIIIIIIIIIIIIIIIIIIIIIIIIII",   # 37
    "IIIIIIIIIIIIIIIIIIIIIIIIZZZZIIIIIIIIIIIIIIIIIIIII",   # 38
    "IIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIZZZZIIIIIIIIIIIIII",   # 39
    "IIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIZZZZIIIIIII",   # 40
    "IIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIZZZZ",   # 41
    "XXXIIIIXXXIIIIIIIIIIIIIIIIXXXIIIIXXXIIIIIIIIIIIII",   # 42
    "XXXIIIIIIIIIIIXXXIIIIIIIIIXXXIIIIIIIIIIIXXXIIIIII",   # 43
    "IIIIIIIIIIIIIIIIIIIIIXXXIIIIXXXIIIIXXXIIIIXXXIIII",   # 44
    "ZZZIIIIZZZIIIIIIIIIIIIIIIIIIZZZIIIIZZZIIIIIIIIIII",   # 45
    "ZZZIIIIIIIIIIIZZZIIIIIIIIIIIZZZIIIIIIIIIIIZZZIIII",   # 46
    "IIIIIIIIIIIIIIIIIIIIIZZZIIIIZZZIIIIZZZIIIIZZZIIII",   # 47
]

# Get positions where each stabilizer has X or Z
def get_positions(s, pauli):
    return [i for i, c in enumerate(s) if c == pauli]

print("Analyzing anticommutation...")
print(f"42 X positions: {get_positions(stabilizers_raw[42], 'X')}")
print(f"43 X positions: {get_positions(stabilizers_raw[43], 'X')}")

# Check which Z stabilizers anticommute
for i, s in enumerate(stabilizers_raw):
    if 'Z' in s and 'X' not in s:
        z_pos = get_positions(s, 'Z')
        x42 = set(get_positions(stabilizers_raw[42], 'X'))
        x43 = set(get_positions(stabilizers_raw[43], 'X'))
        overlap42 = len(x42.intersection(z_pos))
        overlap43 = len(x43.intersection(z_pos))
        if overlap42 % 2 == 1:
            print(f"Stab {i} anticommutes with 42 (overlap {overlap42}): Z at {z_pos}")
        if overlap43 % 2 == 1:
            print(f"Stab {i} anticommutes with 43 (overlap {overlap43}): Z at {z_pos}")

# Find conflicting Z stabilizers
conflicting = set()
for i, s in enumerate(stabilizers_raw):
    if 'Z' in s and 'X' not in s:
        z_pos = set(get_positions(s, 'Z'))
        x42 = set(get_positions(stabilizers_raw[42], 'X'))
        x43 = set(get_positions(stabilizers_raw[43], 'X'))
        if len(x42.intersection(z_pos)) % 2 == 1:
            conflicting.add(i)
        if len(x43.intersection(z_pos)) % 2 == 1:
            conflicting.add(i)

print(f"\nConflicting Z stabilizers: {conflicting}")

# Use all stabilizers except conflicting ones
selected = [i for i in range(len(stabilizers_raw)) if i not in conflicting]
print(f"Selected {len(selected)} stabilizers (removed {len(conflicting)})")

stab_list = [stim.PauliString(stabilizers_raw[i]) for i in selected]
tableau = stim.Tableau.from_stabilizers(stab_list, allow_underconstrained=True)
circuit = tableau.to_circuit(method="graph_state")
print(f"Circuit instructions: {len(circuit)}")

# Clean up
circuit_str = str(circuit).replace('RX', 'H').replace('TICK\n', '')
print("\nCircuit:")
print(circuit_str)

with open('data/gpt5.2/agent_files/candidate_49_v2.stim', 'w') as f:
    f.write(circuit_str)
