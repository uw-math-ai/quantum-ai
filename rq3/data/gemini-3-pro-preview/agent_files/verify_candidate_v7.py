
import stim

def main():
    try:
        # Load baseline
        with open('baseline_rq3_v4.stim', 'r') as f:
            baseline = stim.Circuit(f.read())
            
        # Load candidate
        with open('candidate_fixed.stim', 'r') as f:
            candidate = stim.Circuit(f.read())
            
        t_base = stim.Tableau.from_circuit(baseline)
        t_cand = stim.Tableau.from_circuit(candidate)
        
        # Check generators
        num_qubits = len(t_base)
        all_match = True
        for k in range(num_qubits):
            # The stabilizer of the output state corresponding to Z_k input is z_output(k)
            # z_output(k) is the destabilizer? No, z_output is the stabilizer.
            # wait, tableau maps Z_k to z_output[k].
            # So the stabilizers of the state C|0> are { z_output[k] } for k=0..N-1.
            
            z_base = t_base.z_output(k)
            z_cand = t_cand.z_output(k)
            
            if z_base != z_cand:
                # Check if they differ only by sign
                if z_base.sign != z_cand.sign:
                    # Ignore sign for now
                    # Create copies with positive sign
                    zb = z_base * z_base.sign
                    zc = z_cand * z_cand.sign
                    if zb != zc:
                         print(f"Generator {k} mismatch (not just sign):")
                         print(f"Base: {z_base}")
                         print(f"Cand: {z_cand}")
                         all_match = False
                         break
                else:
                    print(f"Generator {k} mismatch (exact match failed, but sign same? impossible):")
                    all_match = False
                    break
        
        if all_match:
            print("SUCCESS: Tableaus match (up to signs).")
        else:
            print("FAILURE: Tableaus do NOT match.")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
