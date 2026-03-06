import stim
import os
print(f'File: {__file__}')
try:
    with open('candidate_graph.stim', 'r') as f:
        c = stim.Circuit(f.read())
    print(f'Loaded candidate_graph.stim instructions: {len(c)}')
    with open('target_stabilizers.txt', 'r') as f:
        s_list = [l.strip().replace(',','') for l in f if l.strip()]
    print(f'Loaded {len(s_list)} stabilizers')
    
    sim = stim.TableauSimulator()
    sim.do(c)
    preserved = 0
    for s_str in s_list:
        if sim.peek_observable_expectation(stim.PauliString(s_str)) == 1:
            preserved += 1
            
    print(f'Preserved: {preserved}/{len(s_list)}')
    cx = sum(len(op.targets_copy())//2 for op in c if op.name in ['CX', 'CNOT'])
    print(f'CX: {cx}')
except Exception as e:
    print(e)
