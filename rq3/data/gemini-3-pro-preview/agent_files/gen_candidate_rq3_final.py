import stim
import sys

def solve():
    # Read stabilizers
    with open("target_stabilizers_rq3_final.txt", "r") as f:
        stabs_text = f.read().strip()
    
    # Split by comma or newline
    stabilizers = [s.strip() for s in stabs_text.replace('\n', ',').split(',') if s.strip()]
    
    # Create tableau from stabilizers
    try:
        pauli_stabilizers = [stim.PauliString(s) for s in stabilizers]
        
        tableau = stim.Tableau.from_stabilizers(
            pauli_stabilizers, 
            allow_redundant=True, 
            allow_underconstrained=True
        )
    except Exception as e:
        print(f"Error creating tableau: {e}")
        return

    # Synthesize graph state circuit
    circuit = tableau.to_circuit(method="graph_state")
    
    # Replace RX with H
    new_circuit = stim.Circuit()
    for instruction in circuit:
        if instruction.name == "RX":
            new_circuit.append("H", instruction.targets_copy())
        else:
            new_circuit.append(instruction)
            
    # Output the circuit
    print(new_circuit)

if __name__ == "__main__":
    solve()
