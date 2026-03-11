import stim
import numpy as np

def load_stabilizers(filename):
    with open(filename, 'r') as f:
        lines = [line.strip() for line in f if line.strip()]
    return lines

def analyze_stabilizers(stabilizers):
    num_qubits = len(stabilizers[0])
    num_stabilizers = len(stabilizers)
    print(f"Num qubits: {num_qubits}")
    print(f"Num stabilizers: {num_stabilizers}")
    
    # Check if graph state form
    is_graph_state = True
    adj_matrix = np.zeros((num_qubits, num_qubits), dtype=int)
    
    x_positions = []
    
    for k, stab in enumerate(stabilizers):
        # Check if exactly one X and rest are Z or I
        xs = [i for i, char in enumerate(stab) if char == 'X']
        zs = [i for i, char in enumerate(stab) if char == 'Z']
        ys = [i for i, char in enumerate(stab) if char == 'Y']
        
        if len(ys) > 0:
            is_graph_state = False
            # print(f"Stabilizer {k} has Y")
            
        if len(xs) != 1:
            is_graph_state = False
            # print(f"Stabilizer {k} has {len(xs)} Xs")
        else:
            x_pos = xs[0]
            x_positions.append(x_pos)
            for z_pos in zs:
                adj_matrix[x_pos, z_pos] = 1
                adj_matrix[z_pos, x_pos] = 1
                
    if len(set(x_positions)) != len(x_positions):
        print("Multiple stabilizers have X on same qubit (or duplicates).")
        # is_graph_state = False # Not necessarily false, just implies overconstrained or redundant
        
    print(f"Is graph state form directly: {is_graph_state}")
    return is_graph_state, adj_matrix

def synthesize_graph_state(adj_matrix):
    num_qubits = adj_matrix.shape[0]
    circuit = stim.Circuit()
    
    # H on all qubits involved
    # For now, H on all qubits? Or just those in the graph?
    # The stabilizers span the whole space? 
    # Let's just H all 0 to num_qubits-1
    # But wait, we need to map the qubit indices correctly.
    # The stabilizer index corresponds to the qubit index.
    
    # Apply H to all qubits
    circuit.append("H", range(num_qubits))
    
    # Apply CZ for edges
    # Use upper triangle to avoid duplicates
    rows, cols = np.where(np.triu(adj_matrix, k=1))
    for r, c in zip(rows, cols):
        circuit.append("CZ", [r, c])
        
    return circuit

def main():
    stabilizers = load_stabilizers(r"C:\Users\anpaz\Repos\quantum-ai\rq3\data\gemini-3-pro-preview\agent_files\target_stabilizers.txt")
    is_graph, adj = analyze_stabilizers(stabilizers)
    
    if is_graph:
        print("Synthesizing graph state circuit...")
        circuit = synthesize_graph_state(adj)
        with open(r"C:\Users\anpaz\Repos\quantum-ai\rq3\data\gemini-3-pro-preview\agent_files\candidate_graph.stim", "w") as f:
            f.write(str(circuit).replace("tick", "")) # remove ticks if any
    else:
        print("Not directly a graph state. Trying Tableau synthesis.")
        # Create Tableau from stabilizers
        try:
            tableau = stim.Tableau.from_stabilizers(stabilizers, allow_underconstrained=True)
            circuit = tableau.to_circuit(method="graph_state")
            with open(r"C:\Users\anpaz\Repos\quantum-ai\rq3\data\gemini-3-pro-preview\agent_files\candidate_tableau.stim", "w") as f:
                f.write(str(circuit))
        except Exception as e:
            print(f"Tableau synthesis failed: {e}")

if __name__ == "__main__":
    main()
