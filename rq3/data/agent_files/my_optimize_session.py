import stim
import sys

def solve():
    print("Starting synthesis...")
    # Load stabilizers
    try:
        with open('prompt_stabilizers.txt', 'r') as f:
            stabilizers = [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        print("Error: prompt_stabilizers.txt not found.")
        return

    print(f"Loaded {len(stabilizers)} stabilizers.")

    # Graph State Synthesis
    try:
        # allow_redundant=True handles linearly dependent stabilizers
        # allow_underconstrained=True handles cases where fewer than N stabilizers are provided
        tableau = stim.Tableau.from_stabilizers(
            [stim.PauliString(s) for s in stabilizers], 
            allow_redundant=True, 
            allow_underconstrained=True
        )
        circuit = tableau.to_circuit(method="graph_state")
        
        # Post-processing:
        # The graph_state method produces a circuit that prepares the state starting from |0...0>.
        # It uses:
        # - RX gate: Resets qubit to |+> state. Equivalent to H acting on |0>.
        # - R gate: Resets qubit to |0> state. Equivalent to Identity acting on |0>.
        # - MPP gate: Measurement-based preparation.
        # We need to replace these with standard gates if we assume input is |0...0>.
        
        new_circuit = stim.Circuit()
        for instruction in circuit:
            if instruction.name == "RX":
                # RX target means: reset to |+>. 
                # Since start is |0>, H |0> = |+>.
                targets = [t.value for t in instruction.targets_copy()]
                for t in targets:
                    new_circuit.append("H", [t])
            elif instruction.name == "R" or instruction.name == "RZ":
                 # R/RZ target means: reset to |0>.
                 # Since start is |0>, this is a No-Op.
                 pass
            elif instruction.name == "X_ERROR" or instruction.name == "DEPOLARIZE1":
                # Noise channels - should not be here for pure state synthesis, but ignore if present?
                # The prompt says: "Do NOT introduce measurements, resets, or noise"
                # So we skip them.
                pass 
            else:
                new_circuit.append(instruction)
        
        # Verify valid stim
        str_circuit = str(new_circuit)
        
        # Write to candidate file
        with open('candidate.stim', 'w') as f:
            f.write(str_circuit)
            
        print(f"Candidate written to candidate.stim. Gates: {len(new_circuit)}")
        
    except Exception as e:
        print(f"Graph state synthesis failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    solve()
