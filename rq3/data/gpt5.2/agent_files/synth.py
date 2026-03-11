import stim

# Read candidate_graph.stim and convert RX to H
with open(r'C:\Users\anpaz\Repos\quantum-ai\rq3\data\gpt5.2\agent_files\candidate_graph.stim', 'r') as f:
    circ_str = f.read()

# Parse the circuit
circ = stim.Circuit(circ_str)

# Convert RX to H (since starting from |0>)
new_circ_lines = []
for inst in circ:
    if inst.name == 'RX':
        targets = [t.value for t in inst.targets_copy()]
        new_circ_lines.append('H ' + ' '.join(map(str, targets)))
    elif inst.name == 'TICK':
        continue
    else:
        targets = [t.value for t in inst.targets_copy()]
        pairs = []
        for i in range(0, len(targets), 2):
            pairs.append(str(targets[i]) + ' ' + str(targets[i+1]))
        new_circ_lines.append(inst.name + ' ' + ' '.join(pairs))

new_circ_str = '\n'.join(new_circ_lines)

# Parse and verify
new_circ = stim.Circuit(new_circ_str)
cx = sum(1 for inst in new_circ if inst.name == 'CX')
cz = sum(1 for inst in new_circ if inst.name == 'CZ')
h = sum(1 for inst in new_circ if inst.name == 'H')
print(f'CX: {cx}, CZ: {cz}, H: {h}')

# Write clean version
with open(r'C:\Users\anpaz\Repos\quantum-ai\rq3\data\gpt5.2\agent_files\clean_graph.stim', 'w') as f:
    f.write(new_circ_str)

print('Done')
