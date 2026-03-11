import stim
import sys

def get_counts(circuit):
    cx = 0
    vol = 0
    for instr in circuit.flattened():
        targets = instr.targets_copy()
        n_targets = len(targets)
        if instr.name in ['CX', 'CNOT', 'CY', 'CZ', 'SWAP', 'ISWAP']:
            count = n_targets // 2
            if instr.name in ['CX', 'CNOT']:
                cx += count
            vol += count
        elif instr.name in ['H', 'S', 'SQRT_X', 'SQRT_Y', 'SQRT_Z', 'X', 'Y', 'Z', 'I', 'S_DAG', 'SQRT_X_DAG', 'SQRT_Y_DAG', 'SQRT_Z_DAG']:
            vol += n_targets
    return cx, vol

def cz_to_cx(circuit):
    new_circ = stim.Circuit()
    for instr in circuit.flattened():
        if instr.name == 'CZ':
            targets = instr.targets_copy()
            for i in range(0, len(targets), 2):
                c = targets[i]
                t = targets[i+1]
                # CZ c t = H t . CX c t . H t
                new_circ.append('H', [t])
                new_circ.append('CX', [c, t])
                new_circ.append('H', [t])
        elif instr.name == 'CX':
            new_circ.append('CX', instr.targets_copy())
        else:
            new_circ.append(instr.name, instr.targets_copy(), instr.gate_args_copy())
    return new_circ

def main():
    try:
        with open('current_baseline.stim', 'r') as f:
            baseline_text = f.read()
    except FileNotFoundError:
        print("Baseline file not found.")
        return

    baseline = stim.Circuit(baseline_text)
    base_cx, base_vol = get_counts(baseline)
    print(f"Baseline: CX={base_cx}, Vol={base_vol}")

    # Load target stabilizers
    with open('current_target_stabilizers.txt', 'r') as f:
        lines = f.readlines()
    
    target_stabilizers = []
    for line in lines:
        parts = line.strip().split(',')
        for p in parts:
            if p.strip():
                target_stabilizers.append(p.strip())

    print(f"Loaded {len(target_stabilizers)} target stabilizers.")

    def check_stabilizers(circuit):
        sim = stim.TableauSimulator()
        sim.do(circuit)
        for s in target_stabilizers:
            pauli = stim.PauliString(s)
            if sim.peek_observable_expectation(pauli) != 1:
                return False
        return True

    # Get Tableau from baseline
    sim = stim.TableauSimulator()
    sim.do(baseline)
    current_tableau = sim.current_inverse_tableau().inverse()

    # METHOD 1: Graph State
    try:
        cand_graph = current_tableau.to_circuit(method='graph_state')
        cand_graph_cx = cz_to_cx(cand_graph)
        
        cx, vol = get_counts(cand_graph_cx)
        valid = check_stabilizers(cand_graph_cx)
        print(f"Candidate (graph_state): CX={cx}, Vol={vol}, Valid={valid}")
        
        with open('candidate_graph_clean.stim', 'w') as f:
            f.write(str(cand_graph_cx).replace('\n', '\n'))

    except Exception as e:
        print(f"Graph state failed: {e}")

    # METHOD 2: Elimination
    try:
        cand_elim = current_tableau.to_circuit(method='elimination')
        cx, vol = get_counts(cand_elim)
        valid = check_stabilizers(cand_elim)
        print(f"Candidate (elimination): CX={cx}, Vol={vol}, Valid={valid}")
        
        with open('candidate_elim_v4.stim', 'w') as f:
            f.write(str(cand_elim))

    except Exception as e:
        print(f"Elimination failed: {e}")

if __name__ == "__main__":
    main()
