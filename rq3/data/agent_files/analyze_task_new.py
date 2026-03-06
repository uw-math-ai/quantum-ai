import stim

def count_metrics(circuit):
    real_cx = 0
    real_vol = 0
    for instr in circuit:
        n_args = len(instr.targets_copy())
        if instr.name == 'CX' or instr.name == 'CNOT':
            real_cx += n_args // 2
            real_vol += n_args // 2
        elif instr.name in ['CZ', 'CY', 'SWAP']:
            real_vol += n_args // 2
        elif instr.name in ['H', 'S', 'S_DAG', 'SQRT_X', 'SQRT_X_DAG', 'SQRT_Y', 'SQRT_Y_DAG', 'X', 'Y', 'Z', 'I']:
            real_vol += n_args
    return real_cx, real_vol

def check_stabilizers(circuit, stabilizers):
    sim = stim.TableauSimulator()
    sim.do_circuit(circuit)
    preserved = 0
    for s_str in stabilizers:
        s = stim.PauliString(s_str)
        if sim.peek_observable_expectation(s) == 1:
            preserved += 1
    return preserved, len(stabilizers)

def main():
    print("Running version 3")
    with open('current_baseline.stim', 'r') as f:
        baseline_text = f.read()
    baseline = stim.Circuit(baseline_text)
    with open('target_stabilizers.txt', 'r') as f:
        stabilizers = [line.strip() for line in f if line.strip()]
    base_cx, base_vol = count_metrics(baseline)
    print(f'Baseline: CX={base_cx}, Vol={base_vol}')
    preserved, total = check_stabilizers(baseline, stabilizers)
    print(f'Baseline preserved: {preserved}/{total}')
    print('Synthesizing from stabilizers...')
    try:
        tableau = stim.Tableau.from_stabilizers([stim.PauliString(s) for s in stabilizers], allow_underconstrained=True)
    except Exception as e:
        print(f'Error creating tableau: {e}')
        return
    methods = ['elimination', 'graph_state']
    best_cand = None
    best_metrics = (base_cx, base_vol)
    for m in methods:
        try:
            circ = tableau.to_circuit(m)
            cx, vol = count_metrics(circ)
            pres, _ = check_stabilizers(circ, stabilizers)
            print(f'{m}: CX={cx}, Vol={vol}, Preserved={pres}/{total}')
            if pres == total:
                if cx < best_metrics[0] or (cx == best_metrics[0] and vol < best_metrics[1]):
                    best_metrics = (cx, vol)
                    best_cand = circ
        except Exception as e:
            print(f'Error with method {m}: {e}')
    if best_cand:
        print('Strict improvement found!')
        with open('candidate.stim', 'w') as f:
            f.write(str(best_cand))
    else:
        print('No strict improvement found via synthesis.')

if __name__ == '__main__':
    main()
