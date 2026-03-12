
import stim

def main():
    try:
        # Load baseline
        with open('baseline_rq3_v4.stim', 'r') as f:
            baseline = stim.Circuit(f.read())
            
        # Create Tableau
        tableau = stim.Tableau.from_circuit(baseline)
        
        # Synthesize Graph State Circuit (which usually produces RX at start)
        circuit = tableau.to_circuit(method="graph_state")
        
        # We need to replace RX with H, assuming input is |0>.
        # We can iterate over the operations.
        new_circuit = stim.Circuit()
        for op in circuit:
            if op.name == "RX":
                # Replace with H
                new_circuit.append("H", op.targets_copy())
            else:
                new_circuit.append(op)
        
        # Now print nicely formatted output
        # Split multi-qubit gates into smaller chunks
        
        for op in new_circuit:
            if op.name in ["CZ", "CX", "H", "S", "S_DAG", "X", "Y", "Z"]:
                targets = op.targets_copy()
                chunk_size = 4 # small chunk size
                for i in range(0, len(targets), chunk_size):
                    chunk = targets[i:i+chunk_size]
                    # Format: "GATE t1 t2 t3 t4"
                    t_str = " ".join(str(t.value) for t in chunk)
                    print(f"{op.name} {t_str}")
            else:
                print(str(op))

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
