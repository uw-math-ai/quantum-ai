import stim

def synthesize():
    # Read extracted stabilizers
    with open("extracted_stabilizers.txt", "r") as f:
        lines = [l.strip() for l in f if l.strip()]
    
    # Convert to PauliString
    stabilizers = [stim.PauliString(l) for l in lines]
    
    try:
        t = stim.Tableau.from_stabilizers(stabilizers)
        # Synthesize using graph state
        circuit = t.to_circuit(method="graph_state")
        with open("candidate_raw_v2.stim", "w") as f:
            f.write(str(circuit))
        print("Written to candidate_raw_v2.stim")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    synthesize()
