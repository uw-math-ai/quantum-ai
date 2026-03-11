import stim
import sys

def load_stabilizers(filename):
    with open(filename, 'r') as f:
        lines = [line.strip() for line in f if line.strip()]
    return lines

def main():
    stabilizers_path = r"C:\Users\anpaz\Repos\quantum-ai\rq3\data\gemini-3-pro-preview\agent_files\target_stabilizers.txt"
    output_path = r"C:\Users\anpaz\Repos\quantum-ai\rq3\data\gemini-3-pro-preview\agent_files\candidate_tableau.stim"
    
    stabilizers_str = load_stabilizers(stabilizers_path)
    print(f"Loaded {len(stabilizers_str)} stabilizers.")

    stim_stabilizers = []
    for s in stabilizers_str:
        stim_stabilizers.append(stim.PauliString(s))
        
    print("Converted to stim.PauliString.")
    
    try:
        # Create a full tableau from the stabilizers.
        # allow_underconstrained=True fills in the rest.
        tableau = stim.Tableau.from_stabilizers(stim_stabilizers, allow_underconstrained=True)
        print("Created Tableau.")
        
        # Synthesize using graph state method (optimal for CZ count)
        circuit = tableau.to_circuit(method="graph_state")
        print("Synthesized circuit.")
        
        with open(output_path, "w") as f:
            f.write(str(circuit))
        print(f"Tableau synthesis successful. Wrote to {output_path}")
        
    except Exception as e:
        print(f"Tableau synthesis failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
