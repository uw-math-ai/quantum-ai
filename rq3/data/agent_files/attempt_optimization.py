import stim
import sys
import os

def solve():
    print("Loading stabilizers...")
    with open("current_task_stabilizers.txt", "r") as f:
        stabilizers = [line.strip() for line in f if line.strip()]

    print(f"Loaded {len(stabilizers)} stabilizers.")
    
    # Truncate stabilizers to 63 chars if they are longer (assuming extra are 'I')
    # The anomalous line 24 has length 65 but ends with II, so truncating is safe.
    truncated_stabilizers = []
    for s in stabilizers:
        if len(s) > 63:
            truncated_stabilizers.append(s[:63])
        else:
            truncated_stabilizers.append(s)
            
    pauli_stabilizers = [stim.PauliString(s) for s in truncated_stabilizers]
    
    # Create tableau from stabilizers
    # allow_redundant=True just in case, though usually we want independent generators
    # allow_underconstrained=True because we might have fewer stabilizers than qubits
    try:
        tableau = stim.Tableau.from_stabilizers(pauli_stabilizers, allow_redundant=True, allow_underconstrained=True)
    except Exception as e:
        print(f"Error creating tableau: {e}")
        return

    print("Synthesizing circuit with method='graph_state'...")
    try:
        circuit = tableau.to_circuit(method="graph_state")
    except Exception as e:
        print(f"Error synthesizing circuit: {e}")
        return

    # Post-process to replace RX with H
    # Stim's graph state synthesis often starts with RX gates to initialize in X basis.
    # Since we assume start state is |0>, and we want |+>, we replace RX with H.
    # If it uses RY or others, we might need to handle them, but graph states usually use X/Z basis.
    
    new_circuit = stim.Circuit()
    for instruction in circuit:
        if instruction.name == "RX":
            # Replace RX target with H target
            targets = instruction.targets_copy()
            new_circuit.append("H", targets)
        else:
            new_circuit.append(instruction)
            
    # Also check if there are any other resets. 
    # The user said "Do NOT introduce measurements, resets, or noise".
    # If the synthesized circuit has R (Reset Z), and we start in |0>, we can just remove it (since it's already |0>).
    
    final_circuit = stim.Circuit()
    for instruction in new_circuit:
        if instruction.name == "R" or instruction.name == "RZ": # RZ is not a gate in stim, R is reset Z.
            # If it's a reset to 0, and we are at the beginning, we can drop it.
            # But we need to be careful if it's in the middle.
            # Graph state synthesis usually puts initialization at the start.
            continue 
        final_circuit.append(instruction)

    print("Candidate circuit generated.")
    
    # Save candidate to file
    with open("candidate_graph.stim", "w") as f:
        f.write(str(final_circuit))
        
    print("Saved to candidate_graph.stim")
    
if __name__ == "__main__":
    solve()
