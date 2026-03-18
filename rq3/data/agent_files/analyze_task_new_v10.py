import stim

target_stabilizers_str = """
XXIIXXIIIIIIIIIIIIIIIIIIIIII
IIIIIIIXXIIXXIIIIIIIIIIIIIII
IIIIIIIIIIIIIIXXIIXXIIIIIIII
IIIIIIIIIIIIIIIIIIIIIXXIIXXI
XIXIXIXIIIIIIIIIIIIIIIIIIIII
IIIIIIIXIXIXIXIIIIIIIIIIIIII
IIIIIIIIIIIIIIXIXIXIXIIIIIII
IIIIIIIIIIIIIIIIIIIIIXIXIXIX
IIIXXXXIIIIIIIIIIIIIIIIIIIII
IIIIIIIIIIXXXXIIIIIIIIIIIIII
IIIIIIIIIIIIIIIIIXXXXIIIIIII
IIIIIIIIIIIIIIIIIIIIIIIIXXXX
ZZIIZZIIIIIIIIIIIIIIIIIIIIII
IIIIIIIZZIIZZIIIIIIIIIIIIIII
IIIIIIIIIIIIIIZZIIZZIIIIIIII
IIIIIIIIIIIIIIIIIIIIIZZIIZZI
ZIZIZIZIIIIIIIIIIIIIIIIIIIII
IIIIIIIZIZIZIZIIIIIIIIIIIIII
IIIIIIIIIIIIIIZIZIZIZIIIIIII
IIIIIIIIIIIIIIIIIIIIIZIZIZIZ
IIIZZZZIIIIIIIIIIIIIIIIIIIII
IIIIIIIIIIZZZZIIIIIIIIIIIIII
IIIIIIIIIIIIIIIIIZZZZIIIIIII
IIIIIIIIIIIIIIIIIIIIIIIIZZZZ
XXXIIIIXXXIIIIXXXIIIIXXXIIII
ZZZIIIIZZZIIIIZZZIIIIZZZIIII
"""

baseline_stim = """
H 0 8
CX 0 8 0 12 0 16 0 25
H 4 24
CX 4 0 24 0 12 1 1 12 12 1 1 25 24 1 25 2 2 25 25 2 2 16 4 2 13 2 17 2 18 2 19 2 21 2 22 2 23 2 24 2 26 2 27 2 20 3 3 20 20 3 8 3 13 3 16 3 17 3 18 3 19 3 21 3 22 3 23 3 26 3 27 3 4 16 8 4 8 5 5 8 8 5 5 16 16 6 6 16 16 6 13 6 17 6 18 6 19 6 21 6 22 6 23 6 26 6 27 6 8 7 7 8 8 7
H 7 12 20 25
CX 7 12 7 13 7 17 7 20 7 24 7 25 7 26 7 27 12 7 24 7 24 8 8 24 24 8 8 17 8 20 8 25 8 26 8 27 12 8 17 9 9 17 17 9 13 9 21 9 17 10 10 17 17 10
H 10
CX 10 12 10 21 12 11 11 12 12 11 11 13 11 21 13 12 12 13 13 12 12 21 21 13 13 21 21 13 16 14 14 16 16 14
H 14
CX 14 16 14 18 25 14 25 15 15 25 25 15 15 18 15 27 18 16 16 18 18 16 22 16 27 16
H 17
CX 17 22 17 27 18 22 27 18 27 19 19 27 27 19 22 20 20 22 22 20 24 21 21 24 24 21
H 21
CX 21 25 21 27 22 21 22 26 22 27 27 23 23 27 27 23 26 23 27 23
H 24
CX 24 26 24 27 25 27 26 25
"""

def get_counts(circuit):
    num_cx = circuit.num_gates("CX")
    num_cz = circuit.num_gates("CZ")
    # Volume: total gate count in volume gate set
    # Volume gate set: CX, CY, CZ, H, S, SQRT_X, etc.
    # Basically all gates?
    volume = sum(1 for op in circuit.flattened() if op.name in ["CX", "CY", "CZ", "H", "S", "S_DAG", "SQRT_X", "SQRT_X_DAG", "SQRT_Y", "SQRT_Y_DAG", "X", "Y", "Z"])
    return num_cx, num_cz, volume

def check_stabilizers(circuit, stabilizers):
    # Stabilizers are strings like "XXII..."
    # We need to convert them to stim.PauliString
    
    sim = stim.TableauSimulator()
    sim.do(circuit)
    
    preserved = True
    for s_str in stabilizers:
        if not s_str.strip(): continue
        p = stim.PauliString(s_str.strip())
        if sim.peek_observable_expectation(p) != 1:
            preserved = False
            break
    return preserved

def solve():
    baseline = stim.Circuit(baseline_stim)
    stabilizers = [line.strip() for line in target_stabilizers_str.strip().split('\n') if line.strip()]
    
    print(f"Baseline CX: {baseline.num_gates('CX')}")
    print(f"Baseline CZ: {baseline.num_gates('CZ')}")
    cx, cz, vol = get_counts(baseline)
    print(f"Baseline metrics: CX={cx}, Volume={vol}")

    # Check baseline preservation
    is_preserved = check_stabilizers(baseline, stabilizers)
    print(f"Baseline preserved: {is_preserved}")

    # Synthesize new circuit
    # 1. Parse stabilizers to Tableau
    # Since we have n stabilizers for n qubits (26 stabilizers for 28 qubits? No, indices go up to 27)
    # 0..27 is 28 qubits. 26 stabilizers. 28 - 26 = 2 logical qubits?
    # Or maybe it's 28 qubits and 26 stabilizers, so underconstrained.
    
    tableau = stim.Tableau.from_stabilizers([stim.PauliString(s) for s in stabilizers], allow_underconstrained=True)
    
    # 2. Synthesize circuit
    # method='graph_state' usually produces H + CZ + local Cliffords
    try:
        synth_circuit = tableau.to_circuit(method="graph_state")
        
        # 3. Check metrics
        cx_new, cz_new, vol_new = get_counts(synth_circuit)
        print(f"Synthesized (graph_state) metrics: CX={cx_new}, CZ={cz_new}, Volume={vol_new}")
        
        # Verify preservation
        if check_stabilizers(synth_circuit, stabilizers):
            print("Synthesized circuit PRESERVES stabilizers.")
            
            if cx_new < cx or (cx_new == cx and vol_new < vol):
                print("Synthesized circuit is STRICTLY BETTER.")
                with open("solution.stim", "w") as f:
                    f.write(str(synth_circuit))
            else:
                print("Synthesized circuit is NOT better.")
                
                # Try to decompose CZ to CX
                # CZ = H(target) CX H(target)
                # This increases volume but might change CX count if CX was high.
                # But here CX is 0.
                pass
        else:
            print("Synthesized circuit DOES NOT preserve stabilizers (unexpected).")
            
    except Exception as e:
        print(f"Synthesis failed: {e}")

    # Method 2: Elimination
    try:
        synth_circuit_elim = tableau.to_circuit(method="elimination")
        cx_elim, cz_elim, vol_elim = get_counts(synth_circuit_elim)
        print(f"Synthesized (elimination) metrics: CX={cx_elim}, CZ={cz_elim}, Volume={vol_elim}")
        
         # Verify preservation
        if check_stabilizers(synth_circuit_elim, stabilizers):
            print("Elimination circuit PRESERVES stabilizers.")
            if cx_elim < cx: # simple check
                 print("Elimination circuit might be better on CX.")
    except Exception as e:
        print(f"Elimination synthesis failed: {e}")


if __name__ == "__main__":
    solve()
