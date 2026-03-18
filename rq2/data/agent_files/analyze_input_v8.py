
import stim

def parse_and_flatten(filepath):
    with open(filepath, 'r') as f:
        content = f.read()
    
    ops = []
    lines = content.strip().split('\n')
    for line in lines:
        parts = line.strip().split()
        if not parts: continue
        gate = parts[0]
        targets = [int(x) for x in parts[1:]]
        
        if gate == 'CX':
            for i in range(0, len(targets), 2):
                ops.append({'gate': 'CX', 'targets': [targets[i], targets[i+1]]})
        elif gate == 'H':
            for t in targets:
                ops.append({'gate': 'H', 'targets': [t]})
                
    return ops

ops = parse_and_flatten(r'C:\Users\anpaz\Repos\quantum-ai\rq2\input_circuit_v8.stim')

# print(f"Total ops: {len(ops)}")
# for i, op in enumerate(ops):
#    print(f"{i}: {op['gate']} {op['targets']}")

# High degree analysis
control_counts = {}
target_counts = {}
for i, op in enumerate(ops):
    if op['gate'] == 'CX':
        c, t = op['targets']
        if c not in control_counts: control_counts[c] = []
        control_counts[c].append(i)
        if t not in target_counts: target_counts[t] = []
        target_counts[t].append(i)

print("\nTop High-use controls:")
for c, locs in sorted(control_counts.items(), key=lambda x: len(x[1]), reverse=True)[:10]:
    print(f"Qubit {c} used as control {len(locs)} times.")

print("\nTop High-use targets:")
for t, locs in sorted(target_counts.items(), key=lambda x: len(x[1]), reverse=True)[:10]:
    print(f"Qubit {t} used as target {len(locs)} times.")

# Validation failures mapping
# Based on validation output from turn 1
# {"loc": 56, "gate": "CX", "fault_qubit": 5, "fault_pauli": "Z"} -> data_weight 22
# {"loc": 82, "gate": "CX", "fault_qubit": 7, "fault_pauli": "Y"} -> data_weight 21
# {"loc": 9, "gate": "CX", "fault_qubit": 37, "fault_pauli": "Y"} -> data_weight 20

print("\nSpecific failure locations:")
failures = [56, 57, 82, 9, 10, 16]
for loc in failures:
    if loc < len(ops):
        print(f"Loc {loc}: {ops[loc]}")

