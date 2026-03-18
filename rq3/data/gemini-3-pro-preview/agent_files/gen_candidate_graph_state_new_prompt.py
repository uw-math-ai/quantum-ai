import stim

def generate_circuit():
    with open("target_stabilizers_prompt.txt", "r") as f:
        content = f.read().strip()
        # Handle comma separated
        stabs = [s.strip() for s in content.split(',')]
    
    # Create PauliStrings
    paulis = [stim.PauliString(s) for s in stabs]
    
    # Synthesize tableau
    try:
        tableau = stim.Tableau.from_stabilizers(paulis, allow_redundant=True, allow_underconstrained=True)
        # Convert to circuit using graph_state method
        circuit = tableau.to_circuit(method="graph_state")
        
        # Output circuit string
        print(circuit)
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    generate_circuit()
