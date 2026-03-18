import stim

try:
    with open('current_task_stabilizers.txt', 'r') as f:
        lines = [l.strip() for l in f.readlines() if l.strip()]
    
    stabs = []
    for line in lines:
        stabs.append(stim.PauliString(line))
        
    # Create tableau
    # allow_underconstrained=True because we might have fewer than 135 stabilizers (we have 98).
    # allow_redundant=True just in case.
    tab = stim.Tableau.from_stabilizers(stabs, allow_underconstrained=True, allow_redundant=True)
    
    # Synthesize
    circuit = tab.to_circuit(method='graph_state')
    
    # Validate
    sim = stim.TableauSimulator()
    sim.do(circuit)
    failed = 0
    for s in stabs:
        if sim.peek_observable_expectation(s) != 1:
            failed += 1
            
    if failed == 0:
        print('SUCCESS: Circuit preserves all target stabilizers.')
        with open('candidate_from_stabs.stim', 'w') as f:
            f.write(str(circuit))
    else:
        print(f'FAILURE: Circuit failed to preserve {failed} stabilizers.')
        
except Exception as e:
    print(f'Error: {e}')
