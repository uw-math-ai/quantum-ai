import stim

try:
    with open('candidate_from_stabs.stim', 'r') as f:
        lines = f.readlines()
    
    new_lines = []
    for line in lines:
        line = line.strip()
        if not line: continue
        if line.startswith('TICK'): continue
        if line.startswith('RX '):
            line = 'H ' + line[3:]
        new_lines.append(line)
        
    final_circuit_str = '\n'.join(new_lines)
    
    with open('candidate_final.stim', 'w') as f:
        f.write(final_circuit_str)
        
    # Verify again
    c = stim.Circuit(final_circuit_str)
    
    with open('current_task_stabilizers.txt', 'r') as f:
        stabs = [stim.PauliString(l.strip()) for l in f.readlines() if l.strip()]
        
    sim = stim.TableauSimulator()
    sim.do(c)
    
    failed = 0
    for s in stabs:
        if sim.peek_observable_expectation(s) != 1:
            failed += 1
            
    if failed == 0:
        print('SUCCESS: Final circuit verified.')
    else:
        print(f'FAILURE: Final circuit failed {failed} stabilizers.')

except Exception as e:
    print(f'Error: {e}')
