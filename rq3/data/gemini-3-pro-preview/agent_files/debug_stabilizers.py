import stim

def get_stabilizers(circuit):
    sim = stim.TableauSimulator()
    sim.do(circuit)
    # Return the stabilizers of the state
    return sim.current_inverse_tableau().inverse().to_stabilizers()

try:
    with open('current_task_baseline.stim', 'r') as f:
        base_c = stim.Circuit(f.read())
    
    with open('candidate_fixed.stim', 'r') as f:
        cand_c = stim.Circuit(f.read())
        
    base_stabs = get_stabilizers(base_c)
    cand_stabs = get_stabilizers(cand_c)
    
    # Check if they are the same
    # Stabilizers define a group. We need to check if the groups are the same.
    # But usually to_stabilizers() returns a canonical set or generators.
    # A better check is: does cand_c preserve base_stabs?
    
    sim_verify = stim.TableauSimulator()
    sim_verify.do(cand_c)
    
    failed = 0
    for stab in base_stabs:
        if not sim_verify.measure(stab):
            # measure returns result. If +1 stabilizer, result should be False (0) for +1 eigenstate?
            # Wait, measure(P) measures the observable P.
            # If state is +1 eigenstate, result is always 0 (False) (corresponding to +1).
            # If -1 eigenstate, result is 1 (True).
            # If random, result is random.
            # Ideally, expectation should be +1.
            # sim.measure() projects. 
            # Better: sim.peek_observable_expectation(stab)
            
            exp = sim_verify.peek_observable_expectation(stab)
            if exp != 1:
                failed += 1
                
    print(f'Baseline has {len(base_stabs)} stabilizers.')
    print(f'Candidate failed to preserve {failed} stabilizers.')

except Exception as e:
    print(f'Error: {e}')
