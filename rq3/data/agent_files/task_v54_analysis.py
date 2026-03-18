import stim
import sys

def count_metrics(circuit):
    cx = 0
    vol = 0
    for instr in circuit:
        if instr.name in ['CX', 'CNOT']:
            cx += len(instr.targets_copy()) // 2
        
        if instr.name in ['CX', 'CNOT', 'CZ', 'H', 'S', 'SQRT_X', 'X', 'Y', 'Z', 'I']:
             vol += len(instr.targets_copy()) // (2 if instr.name in ['CX', 'CNOT', 'CZ'] else 1)
    return cx, vol

def main():
    try:
        # Load baseline
        with open('task_v54_baseline.stim', 'r') as f:
            baseline_text = f.read()
        baseline = stim.Circuit(baseline_text)
        
        # Load stabilizers
        with open('task_v54_stabilizers.txt', 'r') as f:
            lines = [l.strip() for l in f.readlines() if l.strip()]
        
        num_qubits = len(lines[0])
        print(f"Number of qubits: {num_qubits}")
        print(f"Number of stabilizers: {len(lines)}")
        
        stabilizers = [stim.PauliString(l) for l in lines]
        
        base_cx, base_vol = count_metrics(baseline)
        print(f"Baseline CX: {base_cx}, Volume: {base_vol}")
        
        # Check preservation
        tableau = stim.TableauSimulator()
        tableau.do_circuit(baseline)
        
        failed_indices = []
        for i, s in enumerate(stabilizers):
            if tableau.peek_observable_expectation(s) != 1:
                failed_indices.append(i)
        
        print(f"Baseline preserves {len(stabilizers) - len(failed_indices)}/{len(stabilizers)} stabilizers.")
        if failed_indices:
            print(f"Failed indices: {failed_indices}")

        # Check commutativity manually
        print("\nChecking commutativity...")
        anticommuting_pairs = []
        for i in range(len(stabilizers)):
            for j in range(i + 1, len(stabilizers)):
                if not stabilizers[i].commutes(stabilizers[j]):
                    anticommuting_pairs.append((i, j))
        
        if anticommuting_pairs:
            print(f"Found {len(anticommuting_pairs)} anticommuting pairs.")
            for p in anticommuting_pairs[:5]:
                print(f"Pair {p}: {lines[p[0]]} vs {lines[p[1]]}")
        else:
            print("All stabilizers commute.")

        # Synthesize if consistent
        if not anticommuting_pairs:
            target_tableau = stim.Tableau.from_stabilizers(stabilizers, allow_underconstrained=True)
            synth_circuit = target_tableau.to_circuit(method="elimination")
            
            synth_cx, synth_vol = count_metrics(synth_circuit)
            print(f"Synthesis CX: {synth_cx}, Volume: {synth_vol}")
            
            if synth_cx < base_cx:
                print("Synthesis is BETTER (CX)")
                with open('candidate.stim', 'w') as f:
                     f.write(str(synth_circuit))
            elif synth_cx == base_cx and synth_vol < base_vol:
                print("Synthesis is BETTER (Vol)")
                with open('candidate.stim', 'w') as f:
                     f.write(str(synth_circuit))
            else:
                print("Synthesis is WORSE or EQUAL")
        else:
            print("Cannot synthesize from inconsistent stabilizers.")

            
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
