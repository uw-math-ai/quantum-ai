import stim
import sys

def load_data():
    try:
        circuit = stim.Circuit.from_file(r"data/gemini-3-pro-preview/agent_files_ft/input.stim")
        with open(r"data/gemini-3-pro-preview/agent_files_ft/stabilizers.txt", "r") as f:
            stabilizers = [line.strip() for line in f if line.strip()]
    except:
        circuit = stim.Circuit.from_file(r"C:\Users\anpaz\Repos\quantum-ai\rq2\data\gemini-3-pro-preview\agent_files_ft\input.stim")
        with open(r"C:\Users\anpaz\Repos\quantum-ai\rq2\data\gemini-3-pro-preview\agent_files_ft\stabilizers.txt", "r") as f:
            stabilizers = [line.strip() for line in f if line.strip()]
    return circuit, stabilizers

def main():
    circuit, stab_strings = load_data()
    num_qubits = circuit.num_qubits
    stabilizers = [stim.PauliString(s) for s in stab_strings]
    
    print(f"Circuit: {len(circuit)} lines, {num_qubits} qubits")
    
    sim_ideal = stim.TableauSimulator()
    sim_ideal.do(circuit)
    
    flat_circuit = circuit.flattened()
    
    unique_bad_errors = set()
    bad_fault_details = []

    print("Scanning faults...")
    
    for i in range(len(flat_circuit) + 1):
        if i == len(flat_circuit):
            suffix = stim.Circuit()
        else:
            suffix = stim.Circuit()
            for op in flat_circuit[i:]:
                suffix.append(op)
        
        # Ensure correct size
        suffix.append("I", [num_qubits-1])
        t_suffix = stim.Tableau.from_circuit(suffix)
        
        qubits_to_check = []
        if i == 0:
            qubits_to_check = range(num_qubits)
        else:
            op_prev = flat_circuit[i-1]
            for t in op_prev.targets_copy():
                 if t.is_qubit_target:
                     qubits_to_check.append(t.value)
                     
        if not qubits_to_check:
            continue
            
        for q in qubits_to_check:
            for p_char in ["X", "Z"]:
                if p_char == "X":
                    e = t_suffix.x_output(q)
                else:
                    e = t_suffix.z_output(q)
                
                if e.weight >= 4:
                    exp = sim_ideal.peek_observable_expectation(e)
                    if exp == 0 or exp == -1: # Detectable
                        unique_bad_errors.add(str(e))
                        bad_fault_details.append(str(e))
                        
        if i % 100 == 0:
            print(f"Processed {i}/{len(flat_circuit)}")

    print(f"Unique bad errors: {len(unique_bad_errors)}")
    
    error_objs = [stim.PauliString(s) for s in unique_bad_errors]
    
    # Invert mapping
    stab_to_errors = {}
    for idx, s in enumerate(stabilizers):
        stab_to_errors[idx] = set()

    # Optimized building of cover map
    detectable_errors_count = 0
    undetectable_errors_count = 0
    
    filtered_error_indices = []
    
    for j, e in enumerate(error_objs):
        detected = False
        temp_detectors = []
        for k, s in enumerate(stabilizers):
            if not e.commutes(s):
                temp_detectors.append(k)
                detected = True
        
        if detected:
            detectable_errors_count += 1
            filtered_error_indices.append(j)
            # Add to map
            for k in temp_detectors:
                stab_to_errors[k].add(j)
        else:
            undetectable_errors_count += 1
            print(f"WARNING: Error {j} (weight {e.weight}) undetectable! Assuming global phase.")

    print(f"Detectable: {detectable_errors_count}, Undetectable: {undetectable_errors_count}")
    
    uncovered_errors = set(filtered_error_indices)
    chosen_stabs = []
    
    while uncovered_errors:
        best_stab = -1
        best_count = -1
        best_set = None
        
        for k, errors in stab_to_errors.items():
            intersection = errors.intersection(uncovered_errors)
            count = len(intersection)
            if count > best_count:
                best_count = count
                best_stab = k
                best_set = intersection
        
        if best_count <= 0:
            print("Cannot cover remaining errors!")
            break
            
        chosen_stabs.append(best_stab)
        uncovered_errors -= best_set
        
    print(f"Selected {len(chosen_stabs)} stabilizers to measure.")
    
    with open(r"C:\Users\anpaz\Repos\quantum-ai\rq2\data\gemini-3-pro-preview\agent_files_ft\chosen_stabilizers.txt", "w") as f:
        for k in chosen_stabs:
            f.write(stab_strings[k] + "\n")

if __name__ == "__main__":
    main()
