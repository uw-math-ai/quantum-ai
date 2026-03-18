import stim
import sys

def parse_circuit(text):
    return stim.Circuit(text)

def expand_circuit(circuit):
    expanded = []
    for instr in circuit:
        if instr.name in ["CX", "CNOT", "CY", "CZ", "SWAP", "ISWAP"]:
            targets = instr.targets_copy()
            for i in range(0, len(targets), 2):
                expanded.append(stim.CircuitInstruction(instr.name, targets[i:i+2], instr.gate_args_copy()))
        elif instr.name in ["H", "S", "X", "Y", "Z", "I"]:
            targets = instr.targets_copy()
            for t in targets:
                expanded.append(stim.CircuitInstruction(instr.name, [t], instr.gate_args_copy()))
        else:
             expanded.append(instr)
    return expanded

def count_metrics(circuit):
    cx = 0
    vol = 0
    depth = 0 # Not implementing depth properly, but volume is secondary
    # depth is harder to calculate without a DAG.
    
    for instr in circuit:
        if instr.name in ["CX", "CNOT"]:
            cx += 1
            vol += 1
        elif instr.name in ["SWAP"]:
            # SWAP is 3 CXs usually. But here we treat it as 1 op in volume? 
            # The prompt says: "volume – total gate count in the volume gate set (CX, CY, CZ, H, S, SQRT_X, etc.)"
            # SWAP is usually decomposed into 3 CX. Stim counts SWAP as a gate.
            # But for the comparison, we should probably decompose SWAP to CX for cx_count.
            # The baseline uses CX to implement SWAP.
            # So if I use SWAP gate, I should count it as 3 CXs for cx_count?
            # Prompt says: "cand.cx_count < base.cx_count".
            # If I output SWAP, does the system count it as 3 CX?
            # Safest is to decompose SWAP back to 3 CX if I keep it.
            # But I intend to remove them.
            cx += 3
            vol += 3 # ?
        else:
            vol += 1
            
    return cx, vol

def identify_swaps(instructions):
    # Pass to replace 3 CXs with SWAP
    new_instrs = []
    i = 0
    while i < len(instructions):
        # Check for 3 CXs
        if i + 2 < len(instructions):
            op1 = instructions[i]
            op2 = instructions[i+1]
            op3 = instructions[i+2]
            if op1.name == "CX" and op2.name == "CX" and op3.name == "CX":
                t1 = op1.targets_copy()
                t2 = op2.targets_copy()
                t3 = op3.targets_copy()
                # Check indices
                # CX a b; CX b a; CX a b -> SWAP a b
                a, b = t1[0].value, t1[1].value
                if (t2[0].value == b and t2[1].value == a and
                    t3[0].value == a and t3[1].value == b):
                    new_instrs.append(stim.CircuitInstruction("SWAP", [t1[0], t1[1]]))
                    i += 3
                    continue
        new_instrs.append(instructions[i])
        i += 1
    return new_instrs

def push_swaps_to_start(instructions):
    # Iterate backwards
    # map[logical] = physical
    # We maintain a permutation P.
    # Initially P[x] = x.
    # If we see SWAP(u, v): P[u], P[v] = P[v], P[u].
    # If we see Gate(u): Gate acts on P[u].
    
    # Wait, my previous derivation:
    # Reverse pass.
    # Pop SWAP(u, v). P becomes P * (u v).
    # Pop G(u). Output G(P[u]).
    
    # Let's verify with trace.
    # [H 0, SWAP 0 1]
    # Reverse: SWAP, H
    # Init P = I.
    # Process SWAP 0 1. P: 0->1, 1->0.
    # Process H 0. Output H(P[0]) = H 1.
    # Result [H 1].
    # Does H 1 equivalent to H 0; SWAP 0 1?
    # H 1 |00> = |0+>.
    # H 0; SWAP 0 1 |00> = |+0> -> |0+>. Yes.
    
    # Example 2: [SWAP 0 1, H 0]
    # Reverse: H 0, SWAP 0 1.
    # Process H 0. P=I. Output H 0.
    # Process SWAP 0 1. P: 0->1, 1->0.
    # Result [H 0].
    # Does H 0 equiv SWAP 0 1; H 0?
    # H 0 |00> = |+0>.
    # SWAP 0 1; H 0 |00> = SWAP (|00>) -> |00> -> H 0 -> |+0>. Yes.
    
    # So this logic holds.
    
    mapping = {} # int -> int
    # Identity default
    
    reversed_output = []
    
    # Scan reversed
    for instr in reversed(instructions):
        if instr.name == "SWAP":
            targets = instr.targets_copy()
            u = targets[0].value
            v = targets[1].value
            
            # Get current mappings
            mu = mapping.get(u, u)
            mv = mapping.get(v, v)
            
            # Update mapping
            # We want to swap the pointers.
            # P_new = P_old * (u v)
            # This effectively swaps the values at u and v?
            # Let's trace carefully.
            # Map tells us "Logical Qubit X is currently at Physical Qubit Y".
            # SWAP u v means Physical u and Physical v are swapped.
            # So whatever Logical Qubit was at u is now at v.
            # whatever Logical Qubit was at v is now at u.
            
            # Find logical qubits mapped to u and v?
            # No, my logic above was simpler:
            # P[k] is the physical qubit that logical k maps to?
            # Let's re-verify: "Process H 0. Output H(P[0])".
            # This implies P maps Logical index (in instruction) to Physical index (in output).
            # "Process SWAP 0 1. P: 0->1, 1->0."
            # This means Logical 0 is now at Physical 1.
            # So if next gate uses Logical 0, we emit gate on Physical 1.
            
            # Update step for SWAP(u, v):
            # We are swapping the PHYSICAL locations u and v.
            # So for every logical k, if P[k] == u, it becomes v.
            # If P[k] == v, it becomes u.
            # But since P is a map, we can just swap the values in the map?
            # Wait. "Process SWAP 0 1". P[0] was 0. P[1] was 1.
            # Now P[0] becomes 1. P[1] becomes 0.
            # What about P[2]=2?
            # Yes.
            # So we swap the VALUES of the map for keys that point to u and v?
            # Or do we swap the KEYS?
            # "P maps Logical to Physical".
            # Instruction has Logical indices (well, indices in the sequence).
            # Wait. The "SWAP 0 1" instruction is on the *current* wires 0 and 1.
            # So it acts on whatever is on wire 0 and wire 1.
            # So yes, it swaps the physical locations.
            # So if logical qubit L was at 0, it is now at 1.
            # So we find L such that P[L] == 0, and update P[L] = 1.
            # And L' such that P[L'] == 1, and update P[L'] = 0.
            # This seems inefficient to search.
            
            # Alternative: P maps CURRENT wire to LOGICAL wire?
            # No, when we emit H(k), we need the current wire for k.
            
            # Let's look at the update rule again.
            # P_new[x] = Swap_uv(P_old[x]).
            # P_old[0] = 0.
            # Swap_01 swaps 0 and 1.
            # P_new[0] = Swap_01(0) = 1.
            # P_new[1] = Swap_01(1) = 0.
            # P_new[2] = Swap_01(2) = 2.
            # So yes, we apply the swap to the VALUES of the map.
            # for k in mapping: mapping[k] = swap(mapping[k]).
            # Efficiently:
            # We can treat mapping as `x -> x` implicitly.
            # But since we need to update ALL keys, we better track all involved qubits.
            # Or just update the ones in `mapping` and handle defaults?
            # Defaults are `k->k`. If `k` is u or v, it changes.
            # If `u` is not in mapping, `mapping[u] = u`.
            # So `mapping[u]` becomes `v`.
            # `mapping[v]` becomes `u`.
            # WAIT.
            # If `mapping[0]` is `0`. We want `mapping[0]` to be `1`.
            # If `mapping[x]` was `u`, it becomes `v`.
            # So we just scan the values?
            # No, we can compose permutations.
            # Let Map M.
            # Update M' = S * M.
            # (S * M)(x) = S(M(x)).
            # Yes. So we apply S to the values of M.
            # But M is sparse?
            # We can initialize M to Identity for all qubits (0..12).
            # Max qubit index is small (12). So dense map is fine.
            
            keys = list(mapping.keys())
            # Ensure u and v are keys
            if u not in mapping: mapping[u] = u
            if v not in mapping: mapping[v] = v
            
            # But we need to update ALL keys that might map to u or v.
            # This implies we should track all active qubits.
            # Or simpler: The permutation is on the range of indices.
            # Since N=12, just maintain array [0..11].
            pass # Handled below with dense array
            
        else:
            # Gate
            targets = instr.targets_copy()
            new_targets = []
            for t in targets:
                # Value in map
                val = mapping.get(t.value, t.value)
                new_targets.append(val)
            
            # Create new instruction
            # targets needs Stim target objects
            stim_targets = []
            for t_val in new_targets:
                stim_targets.append(t_val)
            
            reversed_output.append(stim.CircuitInstruction(instr.name, stim_targets, instr.gate_args_copy()))

    return list(reversed(reversed_output))

def solve():
    with open("data/agent_files/baseline.stim", "r") as f:
        baseline_text = f.read()
    
    # Load stabilizers early
    with open("data/agent_files/stabilizers.txt", "r") as f:
        stabs = [line.strip() for line in f if line.strip()]

    baseline = stim.Circuit(baseline_text)
    expanded = expand_circuit(baseline)
    
    # 1. Identify SWAPs
    with_swaps = identify_swaps(expanded)
    
    # Debug: Check validity of with_swaps
    circuit_with_swaps = stim.Circuit()
    for instr in with_swaps:
        circuit_with_swaps.append(instr)
        
    sim_swaps = stim.TableauSimulator()
    sim_swaps.do(circuit_with_swaps)
    swaps_preserved = 0
    for s_str in stabs:
        if sim_swaps.peek_observable_expectation(stim.PauliString(s_str)) == 1:
            swaps_preserved += 1
    print(f"Swaps-substituted Valid: {swaps_preserved == len(stabs)} ({swaps_preserved}/{len(stabs)})")

    # 2. Push SWAPs to start (and drop them)
    # To do this correctly, we need a dense map.
    # Find max qubit index.
    max_q = 0
    for instr in with_swaps:
        for t in instr.targets_copy():
            if t.value > max_q: max_q = t.value
    
    # Custom push_swaps with dense map
    mapping = {i: i for i in range(max_q + 1)}
    
    reversed_output = []
    
    for instr in reversed(with_swaps):
        if instr.name == "SWAP":
            u = instr.targets_copy()[0].value
            v = instr.targets_copy()[1].value
            
            # Apply swap to all VALUES in mapping
            # mapping[k] = S(mapping[k])
            # This is O(N) per swap. N is small (12). Fine.
            for k in mapping:
                val = mapping[k]
                if val == u:
                    mapping[k] = v
                elif val == v:
                    mapping[k] = u
        else:
             # Gate
            targets = instr.targets_copy()
            new_stim_targets = []
            for t in targets:
                val = mapping[t.value]
                new_stim_targets.append(val)
            reversed_output.append(stim.CircuitInstruction(instr.name, new_stim_targets, instr.gate_args_copy()))
            
    final_list = list(reversed(reversed_output))
    
    # Debug: print mapping
    print("Final Mapping (Logical -> Physical):", mapping)

    
    # Reconstruct circuit
    final_circuit = stim.Circuit()
    for instr in final_list:
        final_circuit.append(instr)
        
    # Validation
    # Load stabilizers
    with open("data/agent_files/stabilizers.txt", "r") as f:
        stabs = [line.strip() for line in f if line.strip()]
        
    # Check Baseline First
    sim_base = stim.TableauSimulator()
    base_circuit = stim.Circuit()
    for instr in expanded:
        base_circuit.append(instr)
    sim_base.do(base_circuit) # expanded is equivalent to baseline
    base_valid = True
    base_preserved = 0
    for s_str in stabs:
        if sim_base.peek_observable_expectation(stim.PauliString(s_str)) == 1:
            base_preserved += 1
        else:
            base_valid = False
            
    print(f"Baseline Valid: {base_valid} ({base_preserved}/{len(stabs)})")

    # Check
    sim = stim.TableauSimulator()
    sim.do(final_circuit)
    valid = True
    preserved_count = 0
    for s_str in stabs:
        if sim.peek_observable_expectation(stim.PauliString(s_str)) == 1:
            preserved_count += 1
        else:
            valid = False
    
    print(f"Valid: {valid} ({preserved_count}/{len(stabs)})")
    
    if valid:
        # Check metrics
        base_cx, base_vol = count_metrics(expanded)
        # For candidate, we need to count properly.
        # final_circuit does not have SWAPs (they were dropped).
        # But expand just in case.
        cand_expanded = expand_circuit(final_circuit)
        cand_cx, cand_vol = count_metrics(cand_expanded)
        
        print(f"Baseline: CX={base_cx}, Vol={base_vol}")
        print(f"Candidate: CX={cand_cx}, Vol={cand_vol}")
        
        if cand_cx < base_cx or (cand_cx == base_cx and cand_vol < base_vol):
            print("Improvement found!")
            with open("data/agent_files/candidate.stim", "w") as f:
                f.write(str(final_circuit))
        else:
            print("No improvement (or equal).")
            # Write anyway if valid, just to have something?
            # No, if not better, we shouldn't submit it.
            # But the user asked for strict improvement.
    else:
        print("Invalid circuit.")

    # Also, verify "peephole" on the new circuit.
    # Cancel adjacent CX a b; CX a b.
    # Simple pass.
    
    if valid:
        optimized = []
        skip = False
        for i in range(len(final_list)):
            if skip:
                skip = False
                continue
            if i + 1 < len(final_list):
                op1 = final_list[i]
                op2 = final_list[i+1]
                if op1.name == op2.name and op1.name == "CX":
                    t1 = op1.targets_copy()
                    t2 = op2.targets_copy()
                    if t1[0].value == t2[0].value and t1[1].value == t2[1].value:
                        # Cancel
                        skip = True
                        continue
            optimized.append(final_list[i])
            
        final_circuit_opt = stim.Circuit()
        for instr in optimized:
            final_circuit_opt.append(instr)
            
        with open("data/agent_files/candidate.stim", "w") as f:
            f.write(str(final_circuit_opt))
            
if __name__ == "__main__":
    solve()
