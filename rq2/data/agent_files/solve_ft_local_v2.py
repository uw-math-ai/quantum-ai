import stim
import sys
import time

def analyze_circuit():
    try:
        with open("input_circuit.stim", "r") as f:
            circuit_str = f.read()
        with open("stabilizers.txt", "r") as f:
            stabilizers = [line.strip() for line in f if line.strip()]
            
        circuit = stim.Circuit(circuit_str)
        print(f"Circuit has {len(circuit)} instructions.")
        
        # Check stabilizers
        print("Checking stabilizers...")
        stabilizers_parsed = [stim.PauliString(s) for s in stabilizers]
        sim = stim.TableauSimulator()
        sim.do(circuit)
        
        preserved = 0
        broken_indices = []
        for i, s in enumerate(stabilizers_parsed):
            if sim.peek_observable_expectation(s) == 1:
                preserved += 1
            else:
                broken_indices.append(i)
        
        print(f"Preserved: {preserved}/{len(stabilizers)}")
        if broken_indices:
            print(f"Broken indices: {broken_indices[:10]}...")
        else:
            print("All stabilizers preserved.")

        # Check FT
        print("Checking Fault Tolerance...")
        data_qubits = list(range(150)) # Assuming 0-149 are data
        flag_qubits = [] # Update this if we add flags
        
        gates = list(circuit)
        num_gates = len(gates)
        print(f"Total gates: {num_gates}")
        
        bad_faults = []
        start_time = time.time()
        
        # We check every gate.
        # But we print progress.
        
        for i in range(num_gates):
            if i % 100 == 0:
                elapsed = time.time() - start_time
                print(f"Processed {i}/{num_gates} gates... {len(bad_faults)} bad faults found. Time: {elapsed:.2f}s")
                if elapsed > 60: # Limit to 60 seconds
                    print("Time limit reached. Stopping scan.")
                    break
            
            gate = gates[i]
            if gate.name not in ["CX", "H", "R", "M", "CZ"]:
                continue
                
            targets = gate.targets_copy()
            for t_idx, t in enumerate(targets):
                if not t.is_qubit_target: continue
                q = t.value
                
                # Check X and Z faults
                for p_char in ["X", "Z"]:
                    # Create circuit slice
                    rest = stim.Circuit()
                    for g in gates[i+1:]:
                        rest.append(g)
                    
                    # Propagate
                    tab = stim.Tableau(circuit.num_qubits)
                    tab.do(rest)
                    
                    p = stim.PauliString(circuit.num_qubits)
                    p[q] = p_char
                    
                    res = tab(p)
                    
                    # Check weight
                    dw = sum(1 for k in data_qubits if res[k] != 0) # 0=I, 1=X, 2=Y, 3=Z
                    fw = sum(1 for k in flag_qubits if res[k] in [1, 2]) # X or Y error on flag
                    
                    flagged = (fw > 0)
                    
                    if dw >= 4 and not flagged:
                        bad_faults.append({
                            "gate_idx": i,
                            "qubit": q,
                            "type": p_char,
                            "dw": dw,
                            "fw": fw
                        })
                        if len(bad_faults) >= 10:
                            break
                if len(bad_faults) >= 10: break
            if len(bad_faults) >= 10: break

        if bad_faults:
            print("Found bad faults (first 10):")
            for f in bad_faults:
                print(f)
        else:
            print("No bad faults found (in this scan)")

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    analyze_circuit()
