import stim
import os

# Paths
STABILIZERS_PATH = r"data\gemini-3-pro-preview\agent_files\target_stabilizers.txt"
BASELINE_PATH = r"data\gemini-3-pro-preview\agent_files\baseline.stim"
OUTPUT_PATH = r"data\gemini-3-pro-preview\agent_files\candidate.stim"

def main():
    # Load stabilizers
    with open(STABILIZERS_PATH) as f:
        stabilizers = [line.strip() for line in f if line.strip()]
    
    print(f"Loaded {len(stabilizers)} stabilizers.")

    # Generate circuit using graph state synthesis
    try:
        # Tableau.from_stabilizers creates a tableau whose stabilizers are the given ones.
        # It assumes the input is |0>...|0>.
        t_new = stim.Tableau.from_stabilizers(
            [stim.PauliString(s) for s in stabilizers],
            allow_redundant=True,
            allow_underconstrained=True
        )
        
        # Synthesize circuit
        # method="graph_state" is known to produce 0 CX gates (uses CZ).
        print("Synthesizing circuit with method='graph_state'...")
        circuit_new = t_new.to_circuit(method="graph_state")
        
        # Replace RX with H
        # RX is a reset to |+> state. If input is |0>, H does the same (Z -> X).
        circuit_final = stim.Circuit()
        for instruction in circuit_new:
            if instruction.name == "RX":
                # Replace RX with H
                circuit_final.append("H", instruction.targets_copy())
            else:
                circuit_final.append(instruction)
                
        # Save candidate
        with open(OUTPUT_PATH, "w") as f:
            f.write(str(circuit_final))
            
        print(f"Generated candidate saved to {OUTPUT_PATH}")
        
        # Print metrics for info
        print("\nCandidate Circuit:")
        print(circuit_final)
        
    except Exception as e:
        print(f"Error generating circuit: {e}")

if __name__ == "__main__":
    main()
