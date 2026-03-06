import stim

def solve():
    try:
        # Use the fixed file
        with open("stabilizers_84_fixed.txt", "r") as f:
            lines = [line.strip() for line in f if line.strip()]

        stabilizers = [stim.PauliString(line) for line in lines]
        print(f"Loaded {len(stabilizers)} stabilizers")

        # Create tableau
        tableau = stim.Tableau.from_stabilizers(stabilizers, allow_underconstrained=True, allow_redundant=True)
        
        # Generate circuit
        circuit = tableau.to_circuit(method="elimination")
        
        with open("circuit_84_fixed.stim", "w") as f:
            f.write(str(circuit))
            
        print("Circuit saved to circuit_84_fixed.stim")
        print("Circuit length:", len(circuit))
        print("Num qubits:", circuit.num_qubits)

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    solve()
