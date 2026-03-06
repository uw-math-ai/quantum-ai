import stim
import sys

def count_cx(circuit):
    count = 0
    for instr in circuit:
        if instr.name in ["CX", "CNOT"]:
            count += len(instr.targets_copy()) // 2
    return count

def calculate_volume(circuit):
    count = 0
    for instr in circuit:
        if instr.name in ["CX", "CNOT", "CY", "CZ", "H", "S", "S_DAG", "SQRT_X", "SQRT_X_DAG", "SQRT_Y", "SQRT_Y_DAG", "SQRT_Z", "SQRT_Z_DAG", "X", "Y", "Z", "I"]:
            if instr.name in ["CX", "CNOT", "CY", "CZ"]:
                count += len(instr.targets_copy()) // 2
            else:
                count += len(instr.targets_copy())
    return count

def main():
    try:
        circuit_text = open("baseline.stim").read()
        baseline = stim.Circuit(circuit_text)
        
        cx_base = count_cx(baseline)
        vol_base = calculate_volume(baseline)
        print(f"Baseline: cx={cx_base}, vol={vol_base}")

        with open("target_stabilizers.txt", "r") as f:
            lines = [line.strip() for line in f if line.strip()]
        
        stabilizers = [stim.PauliString(s) for s in lines]
        
        # Create tableau from stabilizers
        # allow_underconstrained=True because we might have fewer stabilizers than qubits?
        # The prompt lists 54 stabilizers. The baseline has 54 qubits (0-53).
        # So it should be fully constrained (unless some are dependent).
        
        try:
            tableau = stim.Tableau.from_stabilizers(stabilizers, allow_underconstrained=True)
        except Exception as e:
            print(f"Error creating tableau: {e}")
            return

        # Synthesize using standard elimination
        elim_circuit = tableau.to_circuit("elimination")
        cx_elim = count_cx(elim_circuit)
        vol_elim = calculate_volume(elim_circuit)
        print(f"Elimination: cx={cx_elim}, vol={vol_elim}")
        
        # Synthesize using graph state method? Not directly available as method string in all versions.
        # But 'graph_state' IS a method in recent stim versions.
        try:
            graph_circuit = tableau.to_circuit("graph_state")
            cx_graph = count_cx(graph_circuit)
            vol_graph = calculate_volume(graph_circuit)
            print(f"Graph State: cx={cx_graph}, vol={vol_graph}")
        except:
            print("Graph state synthesis failed or not supported.")
            graph_circuit = elim_circuit
            cx_graph = cx_elim
            vol_graph = vol_elim

        best_circuit = elim_circuit
        cx_best = cx_elim
        vol_best = vol_elim
        
        if (cx_graph < cx_best) or (cx_graph == cx_best and vol_graph < vol_best):
            best_circuit = graph_circuit
            cx_best = cx_graph
            vol_best = vol_graph
            
        if (cx_best < cx_base) or (cx_best == cx_base and vol_best < vol_base):
            print("FOUND BETTER CIRCUIT!")
            with open("candidate.stim", "w") as f:
                f.write(str(best_circuit))
        else:
            print("No better circuit found.")
            # Still save the best we found
            with open("candidate_failed.stim", "w") as f:
                f.write(str(best_circuit))

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
