import stim
import os

def generate_optimized():
    with open("baseline_correct.stim", "r") as f:
        baseline_text = f.read()

    print(f"Loaded baseline. Length: {len(baseline_text)}")
    
    # Simulate to get tableau
    circuit = stim.Circuit(baseline_text)
    sim = stim.TableauSimulator()
    sim.do(circuit)
    tableau = sim.current_inverse_tableau().inverse()
    
    # Method 1: Graph state
    print("Generating graph state circuit...")
    graph_circuit = tableau.to_circuit(method="graph_state")
    
    # Replace RX with H
    graph_str = str(graph_circuit).replace("RX", "H")
    
    # Method 2: Elimination
    print("Generating elimination circuit...")
    elim_circuit = tableau.to_circuit(method="elimination")
    
    # Replace RX with H in elimination circuit too just in case
    elim_str = str(elim_circuit).replace("RX", "H")

    return graph_str, elim_str

if __name__ == "__main__":
    g_str, e_str = generate_optimized()
    
    with open("candidate_graph.stim", "w") as f:
        f.write(g_str)
        
    with open("candidate_elimination.stim", "w") as f:
        f.write(e_str)
        
    print("Generated candidate_graph.stim and candidate_elimination.stim")
