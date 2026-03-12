import stim
import sys

def synthesize_optimal():
    try:
        # Load baseline
        with open("current_baseline.stim", "r") as f:
            baseline_text = f.read()
        
        baseline = stim.Circuit(baseline_text)
        
        # Simulate to get the tableau
        # We want the state stabilizers, so we simulate from |0> and get the tableau
        sim = stim.TableauSimulator()
        sim.do(baseline)
        
        # The tableau T maps Z bases to stabilizers.
        # T |0> = current state
        # method='graph_state' synthesizes a circuit for the state stabilized by T's stabilizers
        tableau = sim.current_inverse_tableau().inverse()
        
        # Synthesize optimized circuit
        # graph_state method produces CZ + single qubit gates, which is 0 CX count
        optimized = tableau.to_circuit(method="graph_state")
        
        # Post-process:
        # 1. 'graph_state' might produce RX gates which are resets + rotations.
        #    If we are starting from |0> (implied), RX is just H (rotate Z to X).
        #    Wait, RX in Stim usually means Reset X, or Rotation?
        #    Stim's 'RX' is a reset to X state? No, Stim has R_X, R_Y, R_Z (reset).
        #    Actually, standard Stim gates: 'RX' is Reset X? No, 'RX' is Reset X.
        #    'H' is Hadamard.
        #    Wait, `to_circuit` output uses 'H', 'S', 'CZ', 'RX', 'RY', 'RZ'?
        #    No, `graph_state` usually produces 'H', 'S', 'CZ', 'X', 'Y', 'Z'.
        #    It might produce 'RX' (Reset X) if it thinks it needs to reset.
        #    But we are generating a unitary/state prep.
        #    Let's check what 'graph_state' produces.
        #    It produces a circuit that prepares the state.
        #    If it uses 'RX' (reset), it's fine if the qubit starts in arbitrary state.
        #    But we start in |0>.
        #    If the circuit starts with RX, and input is |0>, it means "Prepare |+>".
        #    |0> -- H --> |+>.
        #    RX -- |+>.
        #    So replacing RX with H is correct if input is |0>.
        #    But `graph_state` might also produce `RY`, `RZ`?
        #    Stim documentation says `graph_state` decomposes into H, S, CZ, X, Y, Z.
        #    Wait, `to_circuit` doc says "Returns a circuit that prepares the stabilizer state".
        
        # Let's clean the circuit text
        out_str = str(optimized)
        
        # Replace RX with H, RY with H+S, etc?
        # Actually, if the output contains resets, it assumes we can reset.
        # If the input is known to be |0>, RX is H.
        # RZ is I (since |0> is +1 eigenstate of Z).
        # RY is H S S ? |0> -> |i+> ?
        # Let's assume standard graph state: H on some qubits, CZs between them, then local Cliffords.
        # Typically it starts with resets if it wants to ensure state.
        # Since we start with |0>, we can replace 'R' (Reset Z) with nothing.
        # 'RX' (Reset X) with 'H'.
        # 'RY' (Reset Y) with 'H S'.
        
        lines = []
        for line in out_str.split('\n'):
            line = line.strip()
            if not line: continue
            
            # Simple replacements for resets if we assume input |0>
            # R or RZ -> remove (already |0>)
            # RX -> H (prepare |+>)
            # RY -> H S (prepare |i>) ?? Stim's RY prepares Y basis.
            
            # But wait, does 'graph_state' output resets?
            # Yes, it often starts with R to clear garbage.
            # But we are in a clean |0> state context.
            
            parts = line.split(' ')
            gate = parts[0]
            targets = parts[1:]
            
            if gate == 'R' or gate == 'RZ':
                # Reset to 0. Since we are at 0, do nothing.
                continue
            elif gate == 'RX':
                # Reset to +. From 0, H does 0->+.
                lines.append(f"H {' '.join(targets)}")
            elif gate == 'RY':
                # Reset to +i (Y eigenstate). From 0, H S ?
                # 0 -H-> + -S-> +i
                # So replace with H t; S t
                targs = ' '.join(targets)
                lines.append(f"H {targs}")
                lines.append(f"S {targs}")
            else:
                lines.append(line)
        
        # Reconstruct
        final_circ = '\n'.join(lines)
        
        with open("candidate.stim", "w") as f:
            f.write(final_circ)
        print("Candidate written to candidate.stim")

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)

if __name__ == "__main__":
    synthesize_optimal()
