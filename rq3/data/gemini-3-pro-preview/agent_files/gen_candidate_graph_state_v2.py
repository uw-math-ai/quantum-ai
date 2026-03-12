import stim
import sys

def main():
    stabilizers = []
    try:
        with open('target_stabilizers_new_task.txt', 'r') as f:
            for line in f:
                line = line.strip()
                if line:
                    stabilizers.append(stim.PauliString(line))
    except FileNotFoundError:
        print("target_stabilizers_new_task.txt not found")
        return

    num_qubits = len(stabilizers[0])
    num_stabilizers = len(stabilizers)

    print(f"Num qubits: {num_qubits}")
    print(f"Num stabilizers: {num_stabilizers}")

    try:
        # Create Tableau
        # We use allow_underconstrained=True to let Stim fill the remaining DoF.
        # This is valid because we only need to preserve the given stabilizers.
        tableau = stim.Tableau.from_stabilizers(stabilizers, allow_redundant=True, allow_underconstrained=True)
        print("Tableau created.")
        
        # Synthesize circuit using graph state method (uses CZ, no CX)
        circuit = tableau.to_circuit(method="graph_state")
        print("Circuit synthesized.")
        
        # Replace RX with H
        new_circuit = stim.Circuit()
        for instruction in circuit:
            if instruction.name == "RX":
                targets = instruction.targets_copy()
                new_circuit.append("H", targets)
            elif instruction.name == "R": # Reset Z
                pass
            else:
                new_circuit.append(instruction)
        
        with open("candidate.stim", "w") as f:
            print(new_circuit, file=f)
            
        print("Candidate generated.")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
