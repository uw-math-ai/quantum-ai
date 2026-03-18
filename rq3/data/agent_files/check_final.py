import stim
try:
    with open(r'C:\Users\anpaz\Repos\quantum-ai\rq3\candidate_graph.stim', 'r') as f:
        c = stim.Circuit(f.read())
    with open(r'C:\Users\anpaz\Repos\quantum-ai\rq3\target_stabilizers.txt', 'r') as f:
        s_list = [l.strip().replace(',','') for l in f if l.strip()]
    
    sim = stim.TableauSimulator()
    sim.do(c)
    preserved = 0
    for s_str in s_list:
        if sim.peek_observable_expectation(stim.PauliString(s_str)) == 1:
            preserved += 1
            
    print(f'Preserved: {preserved}/{len(s_list)}')
    
    # CX count
    cx = sum(len(op.targets_copy())//2 for op in c if op.name in ['CX', 'CNOT'])
    print(f'CX: {cx}')

except Exception as e:
    print(e)
