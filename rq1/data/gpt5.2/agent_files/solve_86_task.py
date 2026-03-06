import stim

def solve_86():
    try:
        # Use the original task file which has mixed lengths
        with open("stabilizers_84_task.txt", "r") as f:
            lines = [line.strip() for line in f if line.strip()]
            
        # Pad lines to 86 if they are shorter?
        # Or just use them as is?
        # Stim PauliString automatically pads with I if you combine them? No.
        # But if we create a tableau from them, they must have same length.
        # Stim infers the number of qubits from the longest string.
        # So if we have length 86 strings, the tableau will be 86 qubits.
        # The shorter strings (length 84) will be padded with Is at the end by Stim?
        # Let's verify.
        
        stabilizers = []
        for line in lines:
            stabilizers.append(stim.PauliString(line))
            
        print(f"Loaded {len(stabilizers)} stabilizers")
        # Check lengths
        lens = [len(s) for s in stabilizers]
        print(f"Max length: {max(lens)}")
        
        # Create tableau
        tableau = stim.Tableau.from_stabilizers(stabilizers, allow_underconstrained=True, allow_redundant=True)
        
        # Generate circuit
        circuit = tableau.to_circuit(method="elimination")
        
        with open("circuit_86_task.stim", "w") as f:
            f.write(str(circuit))
            
        print("Circuit saved to circuit_86_task.stim")
        print("Circuit length:", len(circuit))
        print("Num qubits:", circuit.num_qubits)

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    solve_86()
