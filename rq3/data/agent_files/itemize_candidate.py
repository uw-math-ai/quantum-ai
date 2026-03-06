import stim
c = stim.Circuit.from_file('candidate_graph.stim')
for op in c:
    if op.name == 'RX':
        targets = op.targets_copy()
        for i in range(0, len(targets), 20):
             # targets contains GateTarget objects
             print(f'RX' + ''.join(f' {t.value}' for t in targets[i:i+20]))
    elif op.name == 'H' and len(op.targets_copy()) > 20:
         # Split large H layers too if any
        targets = op.targets_copy()
        for i in range(0, len(targets), 20):
             print(f'H' + ''.join(f' {t.value}' for t in targets[i:i+20]))
    elif op.name == 'S' and len(op.targets_copy()) > 20:
        targets = op.targets_copy()
        for i in range(0, len(targets), 20):
             print(f'S' + ''.join(f' {t.value}' for t in targets[i:i+20]))
    elif op.name == 'X' and len(op.targets_copy()) > 20:
        targets = op.targets_copy()
        for i in range(0, len(targets), 20):
             print(f'X' + ''.join(f' {t.value}' for t in targets[i:i+20]))
    elif op.name == 'Y' and len(op.targets_copy()) > 20:
        targets = op.targets_copy()
        for i in range(0, len(targets), 20):
             print(f'Y' + ''.join(f' {t.value}' for t in targets[i:i+20]))
    elif op.name == 'Z' and len(op.targets_copy()) > 20:
        targets = op.targets_copy()
        for i in range(0, len(targets), 20):
             print(f'Z' + ''.join(f' {t.value}' for t in targets[i:i+20]))
    else:
        print(str(op))
