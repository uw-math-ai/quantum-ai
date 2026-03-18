import stim

def get_stabilizers(circuit):
    sim = stim.TableauSimulator()
    sim.do(circuit)
    tab = sim.current_inverse_tableau().inverse()
    stabilizers = []
    for i in range(len(circuit.num_qubits)):
        stabilizers.append(tab.z_output(i))
    return stabilizers

def verify_stabilizers(circuit, stabilizers):
    sim = stim.TableauSimulator()
    sim.do(circuit)
    failed = 0
    for stab in stabilizers:
        # peek_observable_expectation returns +1, -1, or 0 (uncertain)
        if sim.peek_observable_expectation(stab) != 1:
            failed += 1
    return failed

try:
    with open('current_task_baseline.stim', 'r') as f:
        base_c = stim.Circuit(f.read())
    
    # Need to know num_qubits
    nq = base_c.num_qubits
    
    sim_base = stim.TableauSimulator()
    sim_base.do(base_c)
    base_tab = sim_base.current_inverse_tableau().inverse()
    base_stabs = [base_tab.z_output(i) for i in range(nq)]
    
    with open('candidate_fixed.stim', 'r') as f:
        cand_c = stim.Circuit(f.read())
        
    failed = verify_stabilizers(cand_c, base_stabs)
    
    print(f'Baseline num qubits: {nq}')
    print(f'Candidate failed to preserve {failed} stabilizers out of {nq}.')

except Exception as e:
    print(f'Error: {e}')
