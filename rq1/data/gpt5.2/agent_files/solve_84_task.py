import stim
import sys

def solve():
    try:
        with open("stabilizers_84_task.txt", "r") as f:
            lines = [line.strip() for line in f if line.strip()]

        # Parse stabilizers
        stabilizers = []
        for line in lines:
            stabilizers.append(stim.PauliString(line))

        print(f"Loaded {len(stabilizers)} stabilizers")

        # Create tableau
        # allow_underconstrained=True is important if we have fewer stabilizers than qubits (we have 84 stabs for 84 qubits, so maybe full rank)
        # allow_redundant=True in case some are dependent
        tableau = stim.Tableau.from_stabilizers(stabilizers, allow_underconstrained=True, allow_redundant=True)
        
        # Generate circuit
        # "elimination" method creates a circuit that prepares the state
        circuit = tableau.to_circuit(method="elimination")
        
        with open("circuit_84_task.stim", "w") as f:
            f.write(str(circuit))
            
        print("Circuit saved to circuit_84_task.stim")
        print("Circuit length:", len(circuit))

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    solve()
