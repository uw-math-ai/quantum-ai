import stim

def main():
    with open("target_stabilizers_rq3.txt", "r") as f:
        lines = [l.strip() for l in f if l.strip()]
    
    # Clean up commas if present
    lines = [l.replace(',', '') for l in lines]

    stabilizers = [stim.PauliString(l) for l in lines]
    
    # Attempt to create tableau
    try:
        tableau = stim.Tableau.from_stabilizers(stabilizers, allow_underconstrained=True, allow_redundant=True)
    except Exception as e:
        print(f"Error creating tableau: {e}")
        return

    # Synthesize circuit
    # method="graph_state" is the key for low CX count (uses CZ)
    circuit = tableau.to_circuit(method="graph_state")
    
    # Replace RX with H if necessary
    # RX target is a reset X. H on |0> (implicit start) is +.
    # Stim's graph state synthesis often puts RX at the beginning of lines.
    # We want to conform to the rules: no resets unless in baseline.
    # The baseline has no resets.
    # So we replace RX with H.
    
    circuit_str = str(circuit)
    circuit_str = circuit_str.replace("RX", "H")
    
    print(circuit_str)

if __name__ == "__main__":
    main()
