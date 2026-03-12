
import stim

def main():
    try:
        # Load baseline
        with open('baseline_rq3_v4.stim', 'r') as f:
            baseline = stim.Circuit(f.read())
            
        # Create Tableau
        tableau = stim.Tableau.from_circuit(baseline)
        
        # Synthesize Graph State Circuit
        # This produces a circuit that implements the same Clifford unitary (up to phase/framing)
        # graph_state method produces a circuit composed of H, S, CZ, and Pauli gates (for feedback/corrections)
        # It assumes the task is to implement the Clifford operation.
        circuit = tableau.to_circuit(method="graph_state")
        
        # Output
        print(circuit)
        
        # Verify
        t2 = stim.Tableau.from_circuit(circuit)
        if tableau == t2:
            pass # print("Verification: Tableaus match exactly.")
        else:
            print("Verification: Tableaus DO NOT match (might be phase differences).")
            # This is expected for graph state synthesis sometimes (phase fixups)
            # But graph_state usually returns an exact implementation.

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
