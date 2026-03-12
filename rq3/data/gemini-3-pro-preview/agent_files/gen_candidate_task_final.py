import stim

def main():
    try:
        # Load stabilizers
        with open("current_target_stabilizers.txt", "r") as f:
            stabilizers = [line.strip() for line in f if line.strip()]
        
        print(f"Loaded {len(stabilizers)} stabilizers.")
        
        # Create Tableau
        # allow_underconstrained=True is important if stabilizers don't fully specify the state
        # allow_redundant=True is important if stabilizers are not independent
        tableau = stim.Tableau.from_stabilizers(
            [stim.PauliString(s) for s in stabilizers], 
            allow_underconstrained=True,
            allow_redundant=True
        )
        
        # Synthesize circuit
        print("Synthesizing circuit with method='graph_state'...")
        circuit = tableau.to_circuit(method="graph_state")
        
        # Post-process to fix initialization
        new_circuit = stim.Circuit()
        for instruction in circuit:
            if instruction.name == "RX":
                # RX target is a reset to X basis (|+>). H on |0> gives |+>.
                # This is standard initialization for graph states.
                for t in instruction.targets_copy():
                    new_circuit.append("H", [t])
            elif instruction.name in ["R", "RZ"]:
                # Reset to Z basis (|0>). 
                # If we assume the device starts in |0>, this is redundant at the beginning.
                # We'll skip it.
                pass
            else:
                new_circuit.append(instruction)
                
        # Write candidate
        out_path = "candidate_final.stim"
        with open(out_path, "w") as f:
            f.write(str(new_circuit))
            
        print(f"Candidate written to {out_path}")
        
    except Exception as e:
        print(f"Error: {e}")
        exit(1)

if __name__ == "__main__":
    main()
