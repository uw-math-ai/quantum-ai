import stim
import json
import sys

def find_bad_faults():
    circuit = stim.Circuit.from_file(r"C:\Users\anpaz\Repos\quantum-ai\rq2\data\gemini-3-pro-preview\agent_files_ft\circuit.stim")
    num_qubits = circuit.num_qubits
    threshold = (9 - 1) // 2  # 4
    
    # 0. Load stabilizers and prepare filter
    print("Loading stabilizers...")
    with open(r"C:\Users\anpaz\Repos\quantum-ai\rq2\data\gemini-3-pro-preview\agent_files_ft\stabilizers.txt", "r") as f:
        stabilizers = [line.strip() for line in f if line.strip()]
        
    try:
        # Create tableau from stabilizers
        # Note: we need list of PauliString
        stim_stabs = [stim.PauliString(s) for s in stabilizers]
        lengths = [len(s) for s in stim_stabs]
        print(f"Stabilizer lengths: min={min(lengths)}, max={max(lengths)}")
        print(f"Stabilizer length[0]: {len(stim_stabs[0])}")
        stab_tableau = stim.Tableau.from_stabilizers(stim_stabs, allow_redundant=True, allow_underconstrained=True)
        stab_tableau_len = len(stab_tableau)
        print(f"Stab tableau length: {stab_tableau_len}")
        inv_stab_tableau = stab_tableau.inverse()
        num_stabilizers = len(stim_stabs)
        print(f"Loaded {num_stabilizers} stabilizers.")
    except Exception as e:
        print(f"Error loading stabilizers: {e}")
        return

    # 1. Compute total tableau
    print("Computing total tableau...")
    T_total = stim.Tableau.from_circuit(circuit)
    
    # 2. Flatten ops
    ops_list = []
    for op in circuit:
        if op.name == "CX" or op.name == "CNOT":
            t = op.targets_copy()
            for k in range(0, len(t), 2):
                # Create a single instruction for simulation
                ops_list.append( ("CX", [t[k].value, t[k+1].value]) )
        elif op.name in ["H", "X", "Y", "Z", "I"]:
            t = op.targets_copy()
            for k in t:
                ops_list.append( (op.name, [k.value]) )
        else:
            # For other gates, we assume they don't split or we don't analyze inside
            # Just keep as is
            ops_list.append( (op.name, [k.value for k in op.targets_copy()]) )
            
    print(f"Flattened ops length: {len(ops_list)}")
    
    bad_faults = []
    
    # 3. Simulator for prefix
    sim = stim.TableauSimulator()
    # Force simulator to have correct number of qubits
    sim.do(stim.CircuitInstruction("I", [stim.GateTarget(num_qubits-1)]))
    
    print("Simulating...")
    for i, (name, targets) in enumerate(ops_list):
        # Apply gate to simulator
        # Create a tiny circuit or instruction
        # We can use sim.do(stim.CircuitInstruction(name, targets))
        # But constructing CircuitInstruction is tricky with list of ints.
        # stim.CircuitInstruction(name, [stim.GateTarget(t) for t in targets])
        
        # Easier: create a tiny circuit string and parse it? No, slow.
        # Use helper:
        op_targets = [stim.GateTarget(t) for t in targets]
        sim.do(stim.CircuitInstruction(name, op_targets))
        
        # Now check faults *after* this gate
        # Only for Clifford gates of interest
        if name in ["CX", "CNOT", "H", "X", "Y", "Z"]:
            # Get inverse tableau
            inv = sim.current_inverse_tableau()
            
            for q in targets:
                for p_type in ["X", "Z"]:
                    p = stim.PauliString(num_qubits)
                    if p_type == "X":
                        p[q] = "X"
                    else:
                        p[q] = "Z"
                    
                    # Map to input: P_in = inv(P_mid)
                    p_in = inv(p)
                    
                    # Map to output: P_out = T_total(P_in)
                    p_out = T_total(p_in)
                    
                    w = p_out.weight
                    
                    if w >= threshold:
                        # Resize p_out to match stab_tableau length
                        if len(p_out) != stab_tableau_len:
                            # Pad with Identity
                            p_padded = stim.PauliString(stab_tableau_len)
                            # Copy content. slice assignment works?
                            # p_padded[:len(p_out)] = p_out ?
                            # Stim PauliString slicing might be read-only or tricky.
                            # But we can use loop or multiplication.
                            # p_padded = p_out * stim.PauliString(stab_tableau_len) ? No.
                            # Actually, slicing assignment works.
                            try:
                                p_padded[:len(p_out)] = p_out
                                p_check_in = p_padded
                            except:
                                # Fallback
                                p_check_in = stim.PauliString(stab_tableau_len)
                                for i_q in range(len(p_out)):
                                    p_check_in[i_q] = p_out[i_q]
                        else:
                            p_check_in = p_out
                            
                        # Check if it is a stabilizer
                        p_check = inv_stab_tableau(p_check_in)
                        
                        is_stabilizer = True
                        # Check conditions:
                        # 1. Only I or Z components
                        # 2. Identity on logical qubits (indices >= num_stabilizers)
                        # Actually from_stabilizers maps stabilizers to Z_0...Z_{k-1}.
                        # So we check if p_check has only Z/I on 0..k-1 and I elsewhere.
                        
                        for k_idx in range(num_qubits):
                            pauli = p_check[k_idx]
                            if k_idx < num_stabilizers:
                                if pauli == 1 or pauli == 2: # X or Y
                                    is_stabilizer = False
                                    break
                            else:
                                if pauli != 0: # Must be I
                                    is_stabilizer = False
                                    break
                        
                        if not is_stabilizer:
                            bad_faults.append({
                                "op_index": i,
                                "gate": name,
                                "targets": targets,
                                "fault_type": p_type,
                                "qubit": q,
                                "weight": w
                            })
        
        if i % 100 == 0:
            print(f"Processed {i} gates...")

    print(f"Found {len(bad_faults)} bad faults.")
    
    # Save to file
    with open(r"C:\Users\anpaz\Repos\quantum-ai\rq2\data\gemini-3-pro-preview\agent_files_ft\bad_faults.json", "w") as f:
        json.dump(bad_faults, f, indent=2)

if __name__ == "__main__":
    find_bad_faults()
