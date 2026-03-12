import stim

def generate_elimination_solution():
    with open("baseline_current.stim", "r") as f:
        baseline = stim.Circuit(f.read())
    
    sim = stim.TableauSimulator()
    sim.do(baseline)
    tableau = sim.current_inverse_tableau().inverse()
    print(f"Tableau qubits: {len(tableau)}")
    
    # Synthesize using elimination
    # elimination method produces a circuit implementing the unitary
    circuit = tableau.to_circuit(method="elimination")
    
    # cx_count = circuit.num_gates("CX")
    # print(f"Elimination circuit has {cx_count} CX gates.")
    
    with open("candidate_elimination.stim", "w") as f:
        f.write(str(circuit))
    
    try:
        # Try graph state synthesis as well
        gs_circuit = tableau.to_circuit(method="graph_state")
        with open("candidate_gs_unitary.stim", "w") as f:
            f.write(str(gs_circuit))
        print("Graph state synthesis successful.")
    except Exception as e:
        print(f"Graph state synthesis failed: {e}")

if __name__ == "__main__":
    generate_elimination_solution()
