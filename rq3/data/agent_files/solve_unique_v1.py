import stim
import sys

def solve():
    # Read stabilizers
    with open("target_stabilizers_unique_v1.txt", "r") as f:
        lines = [line.strip() for line in f if line.strip()]

    # Convert to Stim Tableau
    try:
        stabilizers = [stim.PauliString(line) for line in lines]
        # Use allow_underconstrained=True because we might have fewer stabilizers than qubits
        tableau = stim.Tableau.from_stabilizers(stabilizers, allow_redundant=True, allow_underconstrained=True)
    except Exception as e:
        print(f"Error parsing stabilizers: {e}")
        return

    # Synthesize circuit using graph state method (produces CZ gates)
    circuit = tableau.to_circuit(method="graph_state")
    
    # Clean the circuit
    clean_circuit = stim.Circuit()
    for instruction in circuit:
        if instruction.name == "RX":
            # RX targets are reset to |+>. 
            # If we start with |0>, H takes us to |+>.
            clean_circuit.append("H", instruction.targets_copy())
        elif instruction.name == "R" or instruction.name == "RZ":
            pass 
        elif instruction.name == "H":
             clean_circuit.append("H", instruction.targets_copy())
        elif instruction.name == "S":
             clean_circuit.append("S", instruction.targets_copy())
        elif instruction.name == "CZ":
             clean_circuit.append("CZ", instruction.targets_copy())
        elif instruction.name == "CX":
             clean_circuit.append("CX", instruction.targets_copy())
        elif instruction.name == "SQRT_X":
             clean_circuit.append("SQRT_X", instruction.targets_copy())
        elif instruction.name == "SQRT_X_DAG":
             clean_circuit.append("SQRT_X_DAG", instruction.targets_copy())
        elif instruction.name == "SQRT_Y":
             clean_circuit.append("SQRT_Y", instruction.targets_copy())
        elif instruction.name == "SQRT_Y_DAG":
             clean_circuit.append("SQRT_Y_DAG", instruction.targets_copy())
        else:
            clean_circuit.append(instruction)

    # Save candidate
    with open("candidate_unique_v1.stim", "w") as f:
        f.write(str(clean_circuit))
    
    print("Generated candidate_unique_v1.stim")

if __name__ == "__main__":
    solve()
