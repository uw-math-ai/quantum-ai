import stim
import sys
import os

def count_cx(circuit):
    count = 0
    for instruction in circuit:
        if instruction.name == "CX" or instruction.name == "CNOT":
            # targets list includes all pairs. For CX 0 1 2 3, length is 4, count is 2.
            try:
                targets = instruction.targets_copy()
            except AttributeError:
                 # Fallback for older versions if needed, or check what is available
                 print(f"DEBUG: instruction attributes: {dir(instruction)}")
                 raise
            count += len(targets) // 2
    return count

def main():
    print("Starting analysis...")
    try:
        with open("current_baseline_task.stim", "r") as f:
            baseline_text = f.read()
        baseline = stim.Circuit(baseline_text)
        b_cx = count_cx(baseline)
        print(f"Baseline CX count: {b_cx}")
        print(f"Baseline gates: {len(baseline)}")
    except Exception as e:
        print(f"Error loading baseline: {e}")
        return

    try:
        with open("current_stabilizers_task.txt", "r") as f:
            lines = [l.strip() for l in f if l.strip()]
        
        if not lines:
            print("No stabilizers found.")
            return
        
        n_qubits = len(lines[0])
        print(f"Number of stabilizers: {len(lines)}")
        print(f"Stabilizer length (qubits): {n_qubits}")

        # Parse stabilizers
        try:
            pauli_strings = [stim.PauliString(s) for s in lines]
            tableau = stim.Tableau.from_stabilizers(pauli_strings, allow_underconstrained=True)
            print("Tableau created successfully.")
        except Exception as e:
            print(f"Failed to create tableau: {e}")
            return
        
        # Synthesize using graph state method
        print("Attempting graph state synthesis...")
        circuit_graph = tableau.to_circuit("graph_state")
        g_cx = count_cx(circuit_graph)
        print(f"Graph State Synthesis CX count: {g_cx}")
        
        # Synthesize using Gaussian elimination
        print("Attempting elimination synthesis...")
        circuit_gauss = tableau.to_circuit("elimination")
        ga_cx = count_cx(circuit_gauss)
        print(f"Elimination Synthesis CX count: {ga_cx}")

        # Choose the best
        candidates = []
        candidates.append((g_cx, circuit_graph, "graph_state"))
        candidates.append((ga_cx, circuit_gauss, "elimination"))
        
        candidates.sort(key=lambda x: x[0])
        
        best_cx, best_circ, method = candidates[0]
        
        print(f"Best synthesized circuit ({method}) has {best_cx} CX gates.")
        
        # Verify preservation locally
        print("Verifying stabilizer preservation locally...")
        sim = stim.TableauSimulator()
        sim.do_circuit(best_circ)
        preserved = True
        for p in pauli_strings:
            if sim.peek_observable_expectation(p) != 1:
                preserved = False
                print(f"Stabilizer not preserved: {p}")
                break
        
        if preserved:
            print("Local verification PASSED.")
            if best_cx < b_cx:
                print("IMPROVEMENT FOUND!")
                with open("candidate.stim", "w") as f:
                    f.write(str(best_circ))
            else:
                print("No improvement from direct synthesis.")
                with open("candidate.stim", "w") as f:
                    f.write(str(best_circ))
        else:
            print("Local verification FAILED.")

    except Exception as e:
        print(f"Analysis failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
