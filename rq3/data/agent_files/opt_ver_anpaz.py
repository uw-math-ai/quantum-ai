import stim
import os

print(f'Running optimization script...')
try:
    with open('candidate_graph.stim', 'r') as f:
        c = stim.Circuit(f.read())
    
    # Optimize: Remove adjacent H gates
    # Since stim.Circuit is not mutable in place easily, we rebuild.
    # But checking adjacency is hard without iteration.
    # We can iterate instructions and buffer them.
    
    new_c = stim.Circuit()
    last_op = {} # qubit -> last_gate_name
    # This is tricky for multi-qubit gates.
    # Simplified approach: Convert to list of ops, then iterate.
    # Since we only care about 1-qubit H cancellation on same qubit.
    # And our circuit is H layer + (H CX H)s + H layer.
    
    # Let's just do a naive pass: if op is H(q) and previous on q was H, cancel.
    # We need to track qubit states.
    
    # Actually, simpler:
    # Just run it as is. CX=205 is better than 289.
    # Volume reduction is secondary.
    # Let's check correctness first.
    
    with open('target_stabilizers.txt', 'r') as f:
        s_list = [l.strip().replace(',','') for l in f if l.strip()]
        
    sim = stim.TableauSimulator()
    sim.do(c)
    preserved = 0
    for s_str in s_list:
        if sim.peek_observable_expectation(stim.PauliString(s_str)) == 1:
            preserved += 1
            
    print(f'Preserved: {preserved}/{len(s_list)}')
    
    cx = sum(len(op.targets_copy())//2 for op in c if op.name in ['CX', 'CNOT'])
    print(f'CX: {cx}')
    
    # Volume
    vol = 0
    for op in c:
        if op.name in ['CX', 'CNOT', 'CZ', 'SWAP']:
            vol += len(op.targets_copy()) // 2
        elif op.name in ['H', 'S', 'X', 'Y', 'Z']:
            vol += len(op.targets_copy())
            
    print(f'Volume: {vol}')
    
    if preserved == len(s_list) and cx < 289:
        print('SUCCESS: Valid and Better!')
    else:
        print('FAILURE: Not strictly better or invalid.')

except Exception as e:
    print(e)
