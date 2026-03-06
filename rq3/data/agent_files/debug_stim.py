import stim

def main():
    try:
        with open("target_stabilizers_119.txt", "r") as f:
            lines = [line.strip() for line in f if line.strip()]
        
        stabilizers = [stim.PauliString(line) for line in lines]
        print(f"Loaded {len(stabilizers)} stabilizers.")
        
        tableau = stim.Tableau.from_stabilizers(stabilizers, allow_redundant=True, allow_underconstrained=True)
        print("Tableau created.")
        
        circuit = tableau.to_circuit(method='graph_state')
        print("Graph state circuit created.")
        print(circuit)

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
