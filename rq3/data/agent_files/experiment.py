import stim
import sys

def count_cx(circuit):
    cx = 0
    for instr in circuit:
        if instr.name == "CX":
            cx += len(instr.targets_copy()) // 2
    return cx

def count_volume(circuit):
    count = 0
    for instr in circuit:
        if instr.name in ["CX", "CY", "CZ", "SWAP", "ISWAP", "ISWAP_DAG"]:
            count += len(instr.targets_copy()) // 2
        elif instr.name in ["H", "S", "S_DAG", "X", "Y", "Z", "I", "SQRT_X", "SQRT_X_DAG", "SQRT_Y", "SQRT_Y_DAG", "SQRT_Z", "SQRT_Z_DAG"]:
            count += len(instr.targets_copy())
    return count

def main():
    try:
        baseline = stim.Circuit.from_file(r"C:\Users\anpaz\Repos\quantum-ai\rq3\data\agent_files\baseline.stim")
    except Exception as e:
        print(f"Failed to load baseline: {e}")
        return

    # Pad baseline to 161 qubits (indices 0..160)
    baseline.append("I", [160])
    
    print(f"Baseline CX: {count_cx(baseline)}")
    print(f"Baseline Vol: {count_volume(baseline)}")
    print(f"Baseline qubits (padded): {baseline.num_qubits}")

    # Load stabilizers
    try:
        with open(r"C:\Users\anpaz\Repos\quantum-ai\rq3\data\agent_files\stabilizers.txt") as f:
            stabilizers = [line.strip().replace(',', '') for line in f if line.strip()]
    except Exception as e:
        print(f"Failed to load stabilizers: {e}")
        return
    
    if not stabilizers:
        print("No stabilizers found.")
        return
        
    print(f"Stabilizer length: {len(stabilizers[0])}")

    # Check if baseline prepares these stabilizers from |0>
    sim = stim.TableauSimulator()
    sim.do(baseline)
    
    expectations = []
    preserved_count = 0
    for s in stabilizers:
        p = stim.PauliString(s)
        exp = sim.peek_observable_expectation(p)
        expectations.append(exp)
        if exp == 1:
            preserved_count += 1
            
    print(f"Preserved {preserved_count}/{len(stabilizers)} stabilizers from |0> input.")
    
    # ALWAYS try to synthesize from stabilizers directly to see if we can beat the baseline
    print("Attempting synthesis from stabilizers...")
    try:
        tableau = stim.Tableau.from_stabilizers(
            [stim.PauliString(s) for s in stabilizers],
            allow_underconstrained=True
        )
        
        # 1. Elimination
        circ_elim = tableau.to_circuit(method="elimination")
        cx_elim = count_cx(circ_elim)
        vol_elim = count_volume(circ_elim)
        print(f"Elimination synthesis: CX={cx_elim}, Vol={vol_elim}")
        
        # 2. Graph State
        circ_graph = tableau.to_circuit(method="graph_state")
        cx_graph = count_cx(circ_graph)
        vol_graph = count_volume(circ_graph)
        print(f"Graph State synthesis: CX={cx_graph}, Vol={vol_graph}")

        # Choose the best
        best_circ = None
        if cx_graph < cx_elim:
            best_circ = circ_graph
            print("Graph state is better.")
        elif cx_graph == cx_elim and vol_graph < vol_elim:
            best_circ = circ_graph
            print("Graph state is better (vol).")
        else:
            best_circ = circ_elim
            print("Elimination is better (or equal).")
            
        # Compare with baseline
        best_cx = count_cx(best_circ)
        best_vol = count_volume(best_circ)
        
        if best_cx < count_cx(baseline) or (best_cx == count_cx(baseline) and best_vol < count_volume(baseline)):
            print("FOUND IMPROVEMENT!")
            with open(r"C:\Users\anpaz\Repos\quantum-ai\rq3\candidate.stim", "w") as f:
                f.write(str(best_circ))
        else:
            print(f"No improvement found via direct synthesis. Best synthesized: CX={best_cx}, Vol={best_vol} vs Baseline: CX={count_cx(baseline)}, Vol={count_volume(baseline)}")
            # Even if not better, save it to inspect/use if we want
            with open(r"C:\Users\anpaz\Repos\quantum-ai\rq3\candidate.stim", "w") as f:
                f.write(str(best_circ))
            
    except Exception as e:
        print(f"Synthesis failed: {e}")

    if preserved_count == len(stabilizers):
        print("Baseline prepares the target stabilizers from |0>.")

    else:
        print("Baseline does NOT prepare the stabilizers from |0>. It might be a logical operation.")
        
        # Check conjugation
        print("Checking conjugation U * S * U^-1...")
        try:
            tableau = stim.Tableau.from_circuit(baseline)
            conj_preserved = 0
            for s in stabilizers:
                p = stim.PauliString(s)
                res = tableau(p)
                if res == p:
                    conj_preserved += 1
            
            print(f"Preserved {conj_preserved}/{len(stabilizers)} by conjugation.")
        except Exception as e:
            print(f"Conjugation check failed: {e}")

if __name__ == "__main__":
    main()
