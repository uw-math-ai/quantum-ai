import stim

def generate_circuit():
    with open(r"C:\Users\anpaz\Repos\quantum-ai\rq3\data\gemini-3-pro-preview\agent_files\my_target_stabilizers.txt", "r") as f:
        lines = f.readlines()
    
    # Clean stabilizers
    cleaned_stabilizers = []
    for line in lines:
        s = line.strip()
        if s:
            cleaned_stabilizers.append(stim.PauliString(s))
            
    try:
        tableau = stim.Tableau.from_stabilizers(cleaned_stabilizers, allow_redundant=True, allow_underconstrained=True)
        
        # Method 1: Graph state
        circuit_graph = tableau.to_circuit("graph_state")
        with open(r"C:\Users\anpaz\Repos\quantum-ai\rq3\data\gemini-3-pro-preview\agent_files\candidate_graph.stim", "w") as f:
            f.write(str(circuit_graph))
            
        # Method 2: Elimination
        circuit_elim = tableau.to_circuit("elimination")
        with open(r"C:\Users\anpaz\Repos\quantum-ai\rq3\data\gemini-3-pro-preview\agent_files\candidate_elim.stim", "w") as f:
            f.write(str(circuit_elim))
            
        print("Circuits generated successfully.")
        
    except Exception as e:
        print(f"Error generating circuit: {e}")

if __name__ == "__main__":
    generate_circuit()
