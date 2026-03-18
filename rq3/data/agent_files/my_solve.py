import stim
import sys

def get_metrics(circuit):
    cx_count = 0
    volume = 0
    for instr in circuit:
        if instr.name in ["CX", "CNOT"]:
            cx_count += len(instr.targets_copy()) // 2
        
        # Volume: Count all gates.
        if instr.name not in ["QUBIT_COORDS", "SHIFT_COORDS", "DETECTOR", "OBSERVABLE_INCLUDE", "TICK", "R", "RX", "RY", "RZ"]:
            if instr.name in ["CX", "CNOT", "CY", "CZ", "SWAP", "ISWAP", "SQRT_XX", "SQRT_YY", "SQRT_ZZ"]:
                volume += len(instr.targets_copy()) // 2
            else:
                volume += len(instr.targets_copy())
                
    return cx_count, volume

def clean_circuit(circuit):
    new_circ = stim.Circuit()
    for instr in circuit:
        if instr.name == "R" or instr.name == "RZ":
            continue
        elif instr.name == "RX":
            # Replace RX target with H target
            for t in instr.targets_copy():
                new_circ.append("H", [t])
        elif instr.name == "RY":
             for t in instr.targets_copy():
                new_circ.append("H", [t])
                new_circ.append("S", [t])
        elif instr.name == "M" or instr.name == "MX" or instr.name == "MY" or instr.name == "MZ":
            # Measurements should not be present in state prep unless explicitly needed?
            # If the original baseline had measurements, we should keep them?
            # The prompt says "Do NOT introduce measurements... unless they already exist".
            # The baseline has no measurements.
            pass
        elif instr.name == "MPP":
             pass
        else:
            new_circ.append(instr)
    return new_circ

def main():
    # Load files
    with open("task_stabilizers.txt", "r") as f:
        stabs_text = f.read().strip()
    stabs = [s.strip() for s in stabs_text.split(",") if s.strip()]

    with open("task_baseline.stim", "r") as f:
        baseline = stim.Circuit(f.read())
        
    b_cx, b_vol = get_metrics(baseline)
    print(f"Baseline: CX={b_cx}, Vol={b_vol}")

    # Create Tableau from Baseline Circuit
    try:
        # pauli_stabs = [stim.PauliString(s) for s in stabs]
        # tableau = stim.Tableau.from_stabilizers(pauli_stabs, allow_underconstrained=True)
        # Instead, trust the baseline circuit
        sim = stim.TableauSimulator()
        sim.do(baseline)
        tableau = sim.current_inverse_tableau() ** -1
        # Or just stim.Tableau.from_circuit(baseline)?
        # stim.Tableau.from_circuit does not exist as a direct method for state prep?
        # stim.Tableau.from_circuit computes the channel tableau.
        # We want the state tableau (stabilizers of the output state).
        # We can use sim.current_inverse_tableau().inverse().
        # But wait, to_circuit uses the tableau as a map from Z to stabilizers.
        # If we have a state stabilized by S_k, we want a tableau T such that T(Z_k) = S_k.
        # The simulator maintains the current state.
        # sim.canonical_stabilizers() returns a list of stabilizers.
        # We can use that?
        # Or better: sim.current_inverse_tableau() gives T^-1 such that T^-1 * state = |0>.
        # So state = T * |0>.
        # So T = sim.current_inverse_tableau().inverse().
        tableau = sim.current_inverse_tableau().inverse()
        print(f"Tableau extracted from baseline. Qubits: {len(tableau)}")
    except Exception as e:
        print(f"Error creating tableau: {e}")
        return

    # Method 1: Graph State
    try:
        raw_graph = tableau.to_circuit(method="graph_state")
        circ_graph = clean_circuit(raw_graph)
        gx, gv = get_metrics(circ_graph)
        print(f"Graph State: CX={gx}, Vol={gv}")
        with open("candidate_graph.stim", "w") as f:
            f.write(str(circ_graph))
    except Exception as e:
        print(f"Graph state failed: {e}")

    # Method 2: Elimination
    try:
        raw_elim = tableau.to_circuit(method="elimination")
        circ_elim = clean_circuit(raw_elim)
        ex, ev = get_metrics(circ_elim)
        print(f"Elimination: CX={ex}, Vol={ev}")
        with open("candidate_elim.stim", "w") as f:
            f.write(str(circ_elim))
    except Exception as e:
        print(f"Elimination failed: {e}")

if __name__ == "__main__":
    main()
