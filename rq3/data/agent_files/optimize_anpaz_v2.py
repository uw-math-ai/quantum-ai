import stim
import re
import sys

def main():
    # Load stabilizers from file
    try:
        with open("target_stabilizers.txt", "r") as f:
            content = f.read()
        
        # Robust parsing using regex to find Pauli strings
        # This ignores commas, newlines, spaces, etc.
        stabs = re.findall(r'[IXYZ]+', content)
        
        # Filter out short matches just in case (e.g. if I is used as a word 'I')
        # But here strings are long.
        stabs = [s for s in stabs if len(s) > 10]
        
        print(f"Found {len(stabs)} stabilizers.")
        if len(stabs) == 0:
            print("Error: No stabilizers found.")
            return

    except Exception as e:
        print(f"Error reading stabilizers: {e}")
        return

    def count_cx(circuit):
        count = 0
        for instr in circuit:
            if instr.name == "CX" or instr.name == "CNOT":
                count += len(instr.targets_copy()) // 2
        return count

    def get_volume(circuit):
        count = 0
        for instr in circuit:
            if instr.name in ["CX", "CNOT", "CY", "CZ", "H", "S", "SQRT_X", "S_DAG", "SQRT_X_DAG", "X", "Y", "Z"]:
                 if instr.name in ["CX", "CNOT", "CY", "CZ"]:
                     count += len(instr.targets_copy()) // 2
                 else:
                     count += len(instr.targets_copy())
        return count

    def check_stabilizers(circuit, stabilizers):
        sim = stim.TableauSimulator()
        try:
            sim.do_circuit(circuit)
            for i, stab in enumerate(stabilizers):
                pauli = stim.PauliString(stab)
                if sim.peek_observable_expectation(pauli) != 1:
                    print(f"Stabilizer {i} failed.")
                    return False
            return True
        except Exception as e:
            print(f"Error checking stabilizers: {e}")
            return False

    # Load baseline
    with open("baseline.stim", "r") as f:
        baseline_text = f.read()
        baseline_circuit = stim.Circuit(baseline_text)
    
    baseline_cx = count_cx(baseline_circuit)
    baseline_vol = get_volume(baseline_circuit)
    print(f"Baseline CX: {baseline_cx}, Volume: {baseline_vol}")
    
    # Create tableau from stabilizers
    try:
        pauli_stabs = [stim.PauliString(s) for s in stabs]
        tableau = stim.Tableau.from_stabilizers(pauli_stabs, allow_redundant=True, allow_underconstrained=True)
    except Exception as e:
        print(f"Error creating tableau: {e}")
        return

    candidates = []

    # Method 1: Graph state synthesis
    try:
        circuit_graph = tableau.to_circuit(method="graph_state")
        cx_graph = count_cx(circuit_graph)
        vol_graph = get_volume(circuit_graph)
        print(f"Graph state synthesis CX: {cx_graph}, Volume: {vol_graph}")
        candidates.append((cx_graph, vol_graph, circuit_graph))
    except Exception as e:
        print(f"Graph state synthesis failed: {e}")

    # Method 2: Elimination synthesis
    try:
        circuit_elim = tableau.to_circuit(method="elimination")
        cx_elim = count_cx(circuit_elim)
        vol_elim = get_volume(circuit_elim)
        print(f"Elimination synthesis CX: {cx_elim}, Volume: {vol_elim}")
        candidates.append((cx_elim, vol_elim, circuit_elim))
    except Exception as e:
        print(f"Elimination synthesis failed: {e}")

    # Sort candidates
    candidates.sort(key=lambda x: (x[0], x[1]))

    best_cand = None
    for cand in candidates:
        cx, vol, circ = cand
        if cx < baseline_cx or (cx == baseline_cx and vol < baseline_vol):
             print(f"Checking candidate with CX={cx}, Vol={vol}...")
             if check_stabilizers(circ, stabs):
                 print("Candidate is better and valid!")
                 best_cand = circ
                 break
             else:
                 print("Candidate failed stabilizer check.")
    
    if best_cand:
        with open("candidate.stim", "w") as f:
            f.write(str(best_cand))
    else:
        print("No better circuit found.")

if __name__ == "__main__":
    main()
