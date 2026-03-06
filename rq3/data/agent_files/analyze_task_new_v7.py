import stim
import sys

def count_cx(circuit):
    count = 0
    for instr in circuit:
        if instr.name == "CX" or instr.name == "CNOT":
            count += len(instr.targets_copy()) // 2
    return count

def get_volume(circuit):
    # Volume is total number of operations
    count = 0
    for instr in circuit:
        if instr.name in ["CX", "CNOT", "CY", "CZ", "H", "S", "SQRT_X", "S_DAG", "SQRT_X_DAG", "X", "Y", "Z", "I"]:
             if instr.name in ["CX", "CNOT", "CY", "CZ"]:
                 count += len(instr.targets_copy()) // 2
             else:
                 count += len(instr.targets_copy())
    return count

def main():
    try:
        with open("current_task_baseline.stim", "r") as f:
            baseline = stim.Circuit(f.read())
        
        print(f"Baseline CX count: {count_cx(baseline)}")
        print(f"Baseline Volume: {get_volume(baseline)}")

        with open("current_task_stabilizers_corrected.txt", "r") as f:
            lines = [l.strip() for l in f if l.strip()]
        
        # Determine number of qubits from the first line length
        num_qubits = len(lines[0])
        print(f"Number of qubits from stabilizers: {num_qubits}")
        
        # Verify baseline qubits
        max_q = 0
        for instr in baseline:
             for t in instr.targets_copy():
                 if t.value > max_q:
                     max_q = t.value
        print(f"Max qubit index in baseline: {max_q}")
        
        if max_q >= num_qubits:
             print("Warning: Baseline uses more qubits than stabilizer length implies.")
             # This implies the stabilizer strings might need to be interpreted carefully or padded?
             # Or maybe the baseline uses auxiliary qubits? But the task is stabilizer preservation.
        
        # Create tableau from stabilizers
        # Note: stim expects Pauli strings like "X0 Z1". The input is "IXZ..."
        # We need to convert "IXZ..." to stim format.
        
        stim_stabilizers = []
        for line in lines:
            stim_stabilizers.append(stim.PauliString(line))
            
        tableau = stim.Tableau.from_stabilizers(stim_stabilizers, allow_underconstrained=True)
        
        # Synthesize using elimination
        circuit_elim = tableau.to_circuit("elimination")
        print(f"Elimination synthesis CX count: {count_cx(circuit_elim)}")
        print(f"Elimination synthesis Volume: {get_volume(circuit_elim)}")
        
        # Synthesize using graph state
        # Graph state synthesis is usually better for CX count
        try:
            circuit_graph = tableau.to_circuit("graph_state")
            print(f"Graph state synthesis CX count: {count_cx(circuit_graph)}")
            print(f"Graph state synthesis Volume: {get_volume(circuit_graph)}")
            
            if count_cx(circuit_graph) < count_cx(baseline):
                 print("Found better circuit with graph state method!")
                 with open("candidate_graph.stim", "w") as f:
                     f.write(str(circuit_graph))
            elif count_cx(circuit_elim) < count_cx(baseline):
                 print("Found better circuit with elimination method!")
                 with open("candidate_elimination.stim", "w") as f:
                     f.write(str(circuit_elim))
            else:
                 print("No trivial improvement found with direct synthesis.")
                 
        except Exception as e:
            print(f"Graph state synthesis failed: {e}")

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
