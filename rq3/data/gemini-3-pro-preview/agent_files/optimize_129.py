import stim

stabilizers = [
    "XXXXXXIII",
    "XXXIIIXXX",
    "ZZIIIIIII",
    "ZIZIIIIII",
    "IIIZZIIII",
    "IIIZIZIII",
    "IIIIIIZZI",
    "IIIIIIZIZ"
]

def synthesize_and_print():
    try:
        # Create Tableau from stabilizers
        stab_paulis = [stim.PauliString(s) for s in stabilizers]
        t = stim.Tableau.from_stabilizers(stab_paulis, allow_redundant=True, allow_underconstrained=True)
        
        # Method 1: Graph State (usually best for CX count)
        circ_graph = t.to_circuit(method="graph_state")
        print("--- CANDIDATE GRAPH STATE ---")
        print(circ_graph)
        
        # Method 2: Elimination
        circ_elim = t.to_circuit(method="elimination")
        print("--- CANDIDATE ELIMINATION ---")
        print(circ_elim)

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    synthesize_and_print()
