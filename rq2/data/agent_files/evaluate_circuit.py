import stim
import sys
from typing import List, Tuple, Set

def get_original_circuit() -> stim.Circuit:
    text = """
    CX 1 0 0 1 1 0
    H 0
    CX 0 2 0 3 0 8
    H 1
    CX 1 0 2 1 1 2 2 1 2 1 3 2 2 3 3 2 3 2 3 4 3 5 7 6 6 7 7 6 6 7 8 6 8 7
    """
    return stim.Circuit(text)

def get_stabilizers() -> List[stim.PauliString]:
    stabs = [
        "XXXXXXIII", "XXXIIIXXX", 
        "ZZIIIIIII", "ZIZIIIIII", 
        "IIIZZIIII", "IIIZIZIII", 
        "IIIIIIZZI", "IIIIIIZIZ"
    ]
    return [stim.PauliString(s) for s in stabs]

def get_all_stabilizers_group(generators: List[stim.PauliString]) -> List[stim.PauliString]:
    # Generate all 2^k elements of the stabilizer group
    # k=8, 2^8=256.
    group = {stim.PauliString("I"*9)}
    for gen in generators:
        new_elements = set()
        for existing in group:
            new_elements.add(existing * gen)
        group.update(new_elements)
    return list(group)

def get_error_weight(error: stim.PauliString, stabilizer_group: List[stim.PauliString]) -> int:
    # Find minimum weight of error * S for all S in group
    min_w = 999
    for s in stabilizer_group:
        combined = error * s
        w = sum(1 for k in range(9) if combined[k] != 0) # Only data qubits 0-8
        if w < min_w:
            min_w = w
    return min_w

def evaluate(candidate_text: str):
    try:
        candidate = stim.Circuit(candidate_text)
    except Exception as e:
        print(f"Error parsing circuit: {e}")
        return

    # 1. Verify stabilizers are preserved
    sim = stim.TableauSimulator()
    sim.do(candidate)
    
    generators = get_stabilizers()
    for g in generators:
        if sim.peek_observable_expectation(g) != 1:
            print(f"STABILIZER FAIL: {g} not preserved")
            # We continue to check FT score anyway, or return?
            # Prompt says "If all stabilizers are preserved... and FT... return"
            # So this is a hard requirement.
            return

    # 2. Fault Tolerance Analysis
    # We need to map faults from Original to Candidate.
    # Assumption: Candidate preserves the "slots" of Original.
    # But how do we find them?
    # We can iterate through the instructions of Original and Candidate in parallel?
    # Or assume Candidate is Original with insertions.
    # To do this robustly, we can build the Candidate by taking Original and inserting things.
    # BUT the user provides a string.
    # We need to know WHICH instruction in Candidate corresponds to the i-th instruction in Original.
    # Heuristic: The n-th occurrence of a gate on specific qubits in Candidate corresponds to the n-th in Original.
    
    orig = get_original_circuit()
    
    # Build a map of (orig_index) -> (cand_index)
    # We iterate both circuits.
    # We look for matches in gate type and targets.
    
    orig_ops = []
    for op in orig:
        if op.name in ["CX", "H", "S", "X", "Y", "Z", "I", "SWAP", "CZ"]:
            targets = op.targets_copy()
            # Decompose multi-target ops for counting
            # e.g. CX 0 1 2 3 -> CX 0 1, CX 2 3
            arity = 2 if op.name in ["CX", "SWAP", "CZ"] else 1
            if arity == 2:
                for k in range(0, len(targets), 2):
                    orig_ops.append((op.name, [t.value for t in targets[k:k+2]]))
            else:
                for t in targets:
                    orig_ops.append((op.name, [t.value for t in targets]))
                    
    cand_ops = []
    cand_op_indices = [] # Map flattened index to original instruction index in Candidate
    for i, op in enumerate(candidate):
        if op.name in ["CX", "H", "S", "X", "Y", "Z", "I", "SWAP", "CZ", "M", "R", "MR"]:
             targets = op.targets_copy()
             arity = 2 if op.name in ["CX", "SWAP", "CZ"] else 1
             if op.name in ["M", "R", "MR"]:
                 # These are ancilla ops usually, or final measurement.
                 # We don't map faults to them (unless they are data ops? but original has no M)
                 continue
             
             if arity == 2:
                for k in range(0, len(targets), 2):
                    cand_ops.append((op.name, [t.value for t in targets[k:k+2]]))
                    cand_op_indices.append(i)
             else:
                for t in targets:
                    cand_ops.append((op.name, [t.value for t in targets]))
                    cand_op_indices.append(i)

    # Now map orig_ops to cand_ops
    # We scan cand_ops and try to match the sequence of orig_ops.
    # We assume orig_ops appear in order in cand_ops, possibly separated by other ops.
    
    mapping = [] # List of indices in cand_ops that correspond to orig_ops
    cand_idx = 0
    for o_op in orig_ops:
        found = False
        while cand_idx < len(cand_ops):
            c_op = cand_ops[cand_idx]
            # Check match: name and targets must match
            if c_op[0] == o_op[0] and c_op[1] == o_op[1]:
                mapping.append(cand_idx)
                found = True
                cand_idx += 1
                break
            cand_idx += 1
        if not found:
            print(f"MAPPING FAIL: Could not find original op {o_op} in candidate.")
            # This might happen if we optimized or reordered.
            # But prompt says "Do not reorder".
            return

    print(f"Mapped {len(mapping)} original operations to candidate.")
    
    # Pre-compute ideal state tableau
    sim_ideal = stim.TableauSimulator()
    sim_ideal.do(candidate) # Should result in code state
    # We can't easily invert the whole channel if it involves measurements.
    # But for error analysis, we can assume the measurements outcome is +1 (0) for ideal?
    # Or just track the Pauli frame relative to ideal.
    
    # Actually, simpler:
    # Run two simulators in parallel.
    # 1. Ideal (no faults).
    # 2. Faulty (with fault).
    # At end, compare data qubits.
    # P_diff = P_fault * P_ideal (bitwise check).
    # This works if they are in the same basis.
    # But better: Use TableauSimulator for both.
    # Get stabilizer group of ideal state.
    # For faulty state, check if it violates stabilizers?
    # No, we need the logical error weight.
    # We need E such that Faulty = E * Ideal.
    # E is a Pauli string.
    # We can find E by:
    #  E = T_fault * T_ideal.inverse() ?
    # This is hard with measurements.
    
    # Alternative:
    # Use FrameSimulator (stim.flipped_measurements_in_circuit_assuming_noiseless_is_correct??)
    # No, we need the state error.
    
    # Let's use the standard "compare tableau" method.
    # Run ideal to get canonical state.
    # Run faulty to get canonical state.
    # They differ by some Pauli P (since only Pauli faults).
    # P = T_fault * T_ideal^-1.
    # We can compute P by tracking the error propagation through the circuit.
    # Initialize error E = I.
    # For each gate G:
    #   E' = G E G^-1
    #   If fault F occurs: E'' = F E'
    # At end, E is the error on the state.
    # Measurements:
    #   If we measure qubit q, and E has X or Y on q, the measurement result flips.
    #   This is the "flag" signal.
    #   Also, the error on q collapses (becomes Z or I).
    #   We need to track this.
    
    # Let's implement Error Propagation Simulator.
    
    stabilizer_group = get_all_stabilizers_group(get_stabilizers())
    
    faults = []
    # Identify all fault locations
    # "For each location l in spots(C)... P in {X,Y,Z}"
    # spots(C) are the mapped locations.
    
    # We iterate through the mapping.
    # mapping[k] is the index in flattened cand_ops.
    # We need to know which MOMENT in the circuit this corresponds to.
    # This is getting complicated because we flattened the ops.
    # Let's step through the circuit gate by gate.
    
    # Flatten candidate into a list of (instruction, targets)
    # But keep track of "op index" to inject faults.
    
    high_weight_unflagged = 0
    total_faults = 0
    
    print("Simulating faults...")
    
    # Iterate over original ops (k)
    for k, cand_flat_idx in enumerate(mapping):
        # The fault occurs "at" this operation.
        # Usually faults are injected "after" the operation?
        # "C[l <- P] ... inserting P at location l".
        # If l is a gate, inserting P means ... before or after?
        # Standard convention: after the gate.
        # Or if "location" is a time slice...
        # Let's assume "after".
        
        # We need to run the circuit.
        # At step cand_flat_idx, we inject P.
        
        target_qubits = cand_ops[cand_flat_idx][1]
        
        for q in target_qubits:
            for p_type in ["X", "Y", "Z"]:
                total_faults += 1
                
                # Simulation
                # We can use Stim's TableauSimulator to propagate the Pauli frame.
                # Or just run two tableaus and compare.
                
                # 1. Ideal run (to get expected measurements)
                sim_ideal = stim.TableauSimulator()
                sim_ideal.do(candidate)
                ideal_meas = sim_ideal.current_measurement_record()
                
                # 2. Faulty run
                sim_fault = stim.TableauSimulator()
                
                # Run up to the fault location
                # We need to execute ops up to cand_flat_idx (inclusive).
                # But `candidate` is a Stim circuit, not flattened.
                # We need to reconstruct the execution sequence.
                
                # Easier approach:
                # Construct a faulty circuit for this specific fault.
                # Then run it.
                
                # We need to insert the fault gate after the specific operation in the candidate.
                # The `cand_op_indices` array maps flat index -> instruction index in `candidate`.
                # Wait, `cand_ops` was flattened.
                # `cand_op_indices` tells us which instruction in `candidate` generated this op.
                # But an instruction might generate multiple ops (e.g. CX 0 1 2 3).
                # If we inject fault after CX 0 1, but before CX 2 3?
                # The prompt says "location l in spots(C)".
                # C has `CX 0 2 0 3 0 8`. This is one line.
                # Does `spots(C)` treat this as 3 separate CNOTs?
                # "CX 0 2 0 3 0 8" is one instruction in Stim.
                # But physically it is 3 gates.
                # The definition of `spots(C)` usually refers to physical locations.
                # My `orig_ops` decomposition broke it down into physical gates.
                # So yes, we treat them as separate.
                # So we must be able to insert faults *between* the decomposed gates if necessary.
                # This implies we should split the candidate circuit instructions if they are merged.
                
                # Since I am generating the candidate, I should avoid merging gates to make this easier.
                # I will ensure the candidate uses 1-pair CNOTs.
                
                # For validation of the USER provided circuit (me), I should parse it.
                # But since I am providing the circuit, I will format it nicely (split gates).
                # But the mapping logic above assumes I can find the ops.
                
                # Let's assume the candidate is already split or I can handle it.
                # To be robust:
                # Re-build the candidate circuit into a list of single operations.
                # Inject fault.
                # Run.
                
                # Rebuild candidate as flat list of single ops
                flat_candidate = []
                for op in candidate:
                     targets = op.targets_copy()
                     arity = 2 if op.name in ["CX", "SWAP", "CZ"] else 1
                     if op.name in ["M", "R", "MR"]:
                          flat_candidate.append((op.name, targets)) # Keep Ms together? Or split?
                          # M 0 1 -> M 0, M 1.
                          # Measurements are usually parallel.
                          # But for simulation it doesn't matter.
                          # Let's split for consistency.
                          for t in targets:
                              flat_candidate.append((op.name, [t]))
                     elif arity == 2:
                        for j in range(0, len(targets), 2):
                            flat_candidate.append((op.name, targets[j:j+2]))
                     else:
                        for t in targets:
                            flat_candidate.append((op.name, [t]))
                            
                # Now `cand_flat_idx` refers to `flat_candidate` index.
                # Inject fault after `flat_candidate[cand_flat_idx]`.
                
                faulty_sim = stim.TableauSimulator()
                
                # Run up to injection
                for i_op in range(cand_flat_idx + 1):
                    op_name, op_targs = flat_candidate[i_op]
                    # Create mini circuit
                    # We need to handle targets correctly (they are stim.GateTarget)
                    # Use .value for integer
                    t_vals = [t.value for t in op_targs]
                    faulty_sim.do(stim.Circuit(f"{op_name} " + " ".join(map(str, t_vals))))
                
                # Inject fault
                faulty_sim.do(stim.Circuit(f"{p_type} {q}"))
                
                # Run rest
                for i_op in range(cand_flat_idx + 1, len(flat_candidate)):
                    op_name, op_targs = flat_candidate[i_op]
                    t_vals = [t.value for t in op_targs]
                    faulty_sim.do(stim.Circuit(f"{op_name} " + " ".join(map(str, t_vals))))
                
                # Check results
                fault_meas = faulty_sim.current_measurement_record()
                
                # Identify flag qubits
                # Flag qubits are those measured?
                # The prompt says "All ancilla qubits must be initialized ... and measured".
                # The data qubits are NOT measured in the circuit (it's a state prep).
                # So ALL measurements are flag measurements.
                # We compare `fault_meas` to `ideal_meas`.
                
                flag_triggered = False
                if len(fault_meas) != len(ideal_meas):
                    print("Error: measurement count mismatch")
                    return
                
                for m_i, m_val in enumerate(fault_meas):
                    if m_val != ideal_meas[m_i]:
                        flag_triggered = True
                        break
                        
                if flag_triggered:
                    continue # Fault tolerated
                
                # If no flag, check error weight on DATA qubits (0-8)
                # Compare faulty state to ideal state
                # Calculate P = T_fault * T_ideal^-1
                # But we can't invert T_ideal easily if measurements involved?
                # Actually, if we assume flags didn't fire, we projected onto the "no error" subspace of the flags?
                # Or rather, the error commuted with the checks.
                
                # To get the error string P:
                # We can trace the Pauli string.
                # Or use the fact that T_fault |0> = P T_ideal |0> (up to phase).
                # We can find P by `sim_ideal.peek_observable_expectation(P_fault_basis)`? No.
                
                # We can just iterate all 4^9 Paulis? No.
                # Use the `canonical_stabilizers`?
                # S_ideal = sim_ideal.canonical_stabilizers()
                # S_fault = faulty_sim.canonical_stabilizers()
                # If P is an error, S_fault should be P S_ideal P^-1.
                # But this doesn't give P uniquely.
                
                # Better way:
                # Initialize a "frame" simulator.
                # Or just compute P by propagating the fault P through the remaining circuit.
                # We assume the circuit operations are Cliffords.
                # Measurements: If result matches ideal (which we conditioned on), 
                # what happens to the Pauli error?
                # If P anticommutes with M, the result would flip.
                # Since result didn't flip, P must commute with M.
                # So P passes through M unchanged (or projected?).
                # If P commutes, it passes through.
                # So we can just propagate P through the rest of the unitary gates.
                # And for measurements, we check commutation.
                # If anticommutes -> Flag would fire.
                # We already checked flags.
                # So we know P commutes with all Ms.
                # So we can just propagate P through the unitary part of the suffix.
                
                # Construct suffix unitary (ignoring measurements, since P commutes)
                suffix_unitary = stim.Circuit()
                for i_op in range(cand_flat_idx + 1, len(flat_candidate)):
                    op_name, op_targs = flat_candidate[i_op]
                    if op_name not in ["M", "R", "MR"]:
                        t_vals = [t.value for t in op_targs]
                        suffix_unitary.append(op_name, t_vals)
                        
                # Propagate P through suffix_unitary
                p_stim = stim.PauliString(sim_ideal.num_qubits) # Max qubits
                # Get max qubits from candidate
                # We can just use 20 to be safe
                nq = 20
                p_stim = stim.PauliString(nq)
                if p_type == "X": p_stim[q] = 1
                elif p_type == "Z": p_stim[q] = 2
                elif p_type == "Y": p_stim[q] = 3
                
                # Use Tableau to propagate
                # T_suffix.inverse() acts on P? No.
                # P_out = T_suffix P_in T_suffix^-1
                # This is `tableau(P)`.
                
                t_suffix = stim.Tableau.from_circuit(suffix_unitary)
                p_out = t_suffix(p_stim)
                
                # Calculate weight on data qubits 0-8
                # We need to reduce p_out by stabilizer group
                
                # Extract X and Z components for 0-8
                # Actually `get_error_weight` does this.
                # We need to slice p_out to 0-8.
                # And verify it commutes with stabilizers?
                # It should, because it's a valid state (just erroneous).
                
                # Construct PauliString for just 0-8
                p_data_str = ""
                for k in range(9):
                    # 0=I, 1=X, 2=Z, 3=Y
                    val = p_out[k]
                    if val == 0: p_data_str += "I"
                    elif val == 1: p_data_str += "X"
                    elif val == 2: p_data_str += "Z"
                    elif val == 3: p_data_str += "Y"
                
                p_data = stim.PauliString(p_data_str)
                
                w = get_error_weight(p_data, stabilizer_group)
                
                if w > 1:
                    # Unflagged high weight error
                    # Check "T(S(C)) non-empty".
                    # We found one.
                    # This reduces score.
                    # score -= 1/|T| ... wait
                    # Formula: FT = 1 - (1/|T|) * count.
                    # If T is all high-weight errors.
                    # This formula says: "Fraction of high-weight errors that are NOT flagged".
                    # So we count (Unflagged & Weight>1).
                    # We also need Total (Weight>1).
                    high_weight_unflagged += 1
                    # print(f"Unflagged error: {p_type} at {k} (q{q}) -> weight {w}")

    # To calculate score, we need the total number of faults that cause >1 error (flagged or not).
    # We can re-run the loop or track it.
    # Let's track it.
    # We need to know if the fault *would have caused* >1 error regardless of flagging.
    # "E(C', C) > t". This E is the error of the circuit.
    # Does "E(C', C)" include the effect of flags?
    # Usually E is the error *after decoding*.
    # But here we don't have a decoder. We have flags.
    # The definition suggests E is the physical error on the state.
    # So yes, we calculate weight W for every fault.
    # T = { faults where W > 1 }.
    # Score = 1 - (Unflagged in T) / |T|.
    
    # So I need to store (flagged, weight) for every fault.
    pass

