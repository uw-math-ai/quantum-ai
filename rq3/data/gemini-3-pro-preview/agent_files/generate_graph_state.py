import stim

def generate_graph_state():
    with open("target_stabilizers.txt", "r") as f:
        lines = [line.strip() for line in f if line.strip()]

    stabilizers = []
    for line in lines:
        stabilizers.append(stim.PauliString(line))

    try:
        # allow_redundant and allow_underconstrained to be safe
        tableau = stim.Tableau.from_stabilizers(stabilizers, allow_redundant=True, allow_underconstrained=True)
        circuit = tableau.to_circuit(method="graph_state")
        
        # Post-process to remove resets if we assume |0> input
        # RX target -> H target (if we assume starting from |0>)
        # R target -> (remove) (if we assume starting from |0>)
        # But let's check what it produces first.
        
        print(circuit)
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    generate_graph_state()
