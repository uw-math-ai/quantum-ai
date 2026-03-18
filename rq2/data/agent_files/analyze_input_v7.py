
import stim

def parse_and_flatten(filepath):
    with open(filepath, 'r') as f:
        content = f.read()
    
    # We want to emulate how validate_circuit likely parses it.
    # It likely iterates over gates and expands targets.
    
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

ops = parse_and_flatten(r'C:\Users\anpaz\Repos\quantum-ai\rq2\input_circuit_v2.stim')

print(f"Total ops: {len(ops)}")
for i, op in enumerate(ops):
    print(f"{i}: {op['gate']} {op['targets']}")

# Identify the locations reported in validation
failures = [56, 57, 82, 9, 10, 16, 11, 26]
print("\nFailures analysis:")
for loc in failures:
    if loc < len(ops):
        print(f"Loc {loc}: {ops[loc]}")

