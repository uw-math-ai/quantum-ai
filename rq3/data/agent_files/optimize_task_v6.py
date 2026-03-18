import stim
import sys

def parse_stabilizers(filename):
    with open(filename, 'r') as f:
        lines = [line.strip() for line in f if line.strip()]
    
    # Filter out empty or malformed lines
    stabs = []
    for line in lines:
        if set(line).issubset({'I', 'X', 'Y', 'Z'}):
            stabs.append(stim.PauliString(line))
    return stabs

def count_cx(circuit):
    count = 0
    for instr in circuit:
        if instr.name == "CX" or instr.name == "CNOT":
            count += len(instr.targets_copy()) // 2
    return count

def get_volume(circuit):
    # Approximating volume as total gates for now, or use specific metric
    # Prompt says: "volume - total gate count in the volume gate set (CX, CY, CZ, H, S, SQRT_X, etc.)"
    count = 0
    for instr in circuit:
        if instr.name in ["CX", "CY", "CZ", "H", "S", "SQRT_X", "X", "Y", "Z", "I"]:
            if instr.name in ["CX", "CY", "CZ"]:
                count += len(instr.targets_copy()) // 2
            else:
                count += len(instr.targets_copy())
    return count

def optimize_circuit_swaps(circuit):
    # Flatten circuit to list of ops
    ops = []
    for instr in circuit:
        if instr.name == "CX":
            targets = instr.targets_copy()
            for i in range(0, len(targets), 2):
                ops.append(("CX", targets[i].value, targets[i+1].value))
        elif instr.name == "H":
            for t in instr.targets_copy():
                ops.append(("H", t.value))
        else:
            # Handle other gates if any
             for t in instr.targets_copy():
                ops.append((instr.name, t.value))
                
    # Optimization pass: Remove SWAPs (CX a b, CX b a, CX a b)
    # Mapping from logical to physical: which physical qubit holds logical qubit q?
    # Initially logical q is at physical q.
    # Actually, tracking "where is the data" is easier.
    # location[q] = physical qubit holding data of logical q.
    
    # Wait, the algorithm I derived earlier:
    # M[i] is the *data source* for the current gate on wire i.
    # If gate is on wire w, it acts on the data M[w].
    # Initial M[i] = i.
    # SWAP(a, b) -> swap(M[a], M[b]). 
    # Normal Gate(a) -> Output Gate(M[a]).
    
    # Let's try this.
    
    # First, max qubit index
    max_q = 0
    for op in ops:
        if op[0] == "CX":
            max_q = max(max_q, op[1], op[2])
        else:
            max_q = max(max_q, op[1])
    
    mapping = {i: i for i in range(max_q + 1)}
    
    new_ops = []
    
    i = 0
    while i < len(ops):
        # Look ahead for SWAP
        is_swap = False
        if i + 2 < len(ops):
            op1 = ops[i]
            op2 = ops[i+1]
            op3 = ops[i+2]
            if op1[0] == "CX" and op2[0] == "CX" and op3[0] == "CX":
                # Check indices
                # CX a b, CX b a, CX a b
                a, b = op1[1], op1[2]
                if op2[1] == b and op2[2] == a and op3[1] == a and op3[2] == b:
                    # Found SWAP(a, b)
                    # Update mapping
                    mapping[a], mapping[b] = mapping[b], mapping[a]
                    i += 3
                    continue
        
        # Not a swap, process gate
        op = ops[i]
        if op[0] == "CX":
            # Output mapped gate
            # Note: The gate physically acts on wire u, v.
            # But we want to preserve the LOGICAL operation.
            # If the original circuit had CX u v, it meant "interact data at u with data at v".
            # The data for u is now at mapping[u]??
            # Let's re-verify.
            
            # Original trace:
            # q0: D0
            # q1: D1
            # SWAP q0 q1.
            # q0 has D1, q1 has D0.
            # CX q0 q1. (Controls D1, targets D0).
            
            # Optimized trace:
            # q0: D0
            # q1: D1
            # (SWAP removed). q0 has D0, q1 has D1.
            # We want to perform "Controls D1, targets D0".
            # D1 is at q1. D0 is at q0.
            # So we should do CX q1 q0.
            
            # Original: CX u v.
            # Optimized: CX (location of data at u) (location of data at v).
            # Where is the data "at u" in the original circuit?
            # It's the data that *would be at u* if we did the swaps.
            # Let's call `tracker[q]` = location of data `q`.
            # Initially `tracker[q] = q`.
            # `SWAP(u, v)`: `tracker[u]` and `tracker[v]` don't change location, but the data *moves*.
            # Data at u moves to v. Data at v moves to u.
            # So `loc(data_u)` becomes `v`. `loc(data_v)` becomes `u`.
            # NO.
            # We are *removing* the physical swaps.
            # So the data *stays* where it is.
            # But the *original circuit* moved it.
            # So the *original circuit's view* of where the data is, changes.
            
            # Let's use the inverse mapping approach.
            # Let `P` be the permutation the original circuit *thinks* has happened.
            # `P[logical_q]` = `physical_q_in_original_circuit`.
            # Initially `P[q] = q`.
            # `SWAP(u, v)` in original circuit:
            # The logical qubit that was at `u` is now at `v`.
            # The logical qubit that was at `v` is now at `u`.
            # So, find `L1` such that `P[L1] == u`. Update `P[L1] = v`.
            # Find `L2` such that `P[L2] == v`. Update `P[L2] = u`.
            
            # When we encounter `CX u v` in original circuit:
            # It acts on physical `u` and `v`.
            # We need to know: "Which logical qubits are at `u` and `v` currently?"
            # `L_u` is the logical qubit at `u`. `L_v` is the logical qubit at `v`.
            # In our *optimized* circuit (no swaps), logical qubit `L` is always at physical qubit `L` (or some other fixed mapping).
            # If we remove all swaps, logical `L` stays at physical `L`.
            # So if the operation is `CX u v` (physical in original),
            # it acts on `L_u` and `L_v`.
            # So we must perform `CX L_u L_v`.
            # Where `L_u` is the logical qubit that is currently at `u` in the original circuit simulation.
            
            # So:
            # `logical_at_physical[p]` = `logical_q`.
            # Init `logical_at_physical[p] = p`.
            # `SWAP(u, v)`:
            # `logical_at_physical[u], logical_at_physical[v] = logical_at_physical[v], logical_at_physical[u]`.
            # Drop the swap.
            # `CX u v`:
            # `lu = logical_at_physical[u]`
            # `lv = logical_at_physical[v]`
            # Output `CX lu lv`.
            
            # This seems correct.
            # If `SWAP(0, 73)` happens:
            # `logical_at_physical` 0 becomes 73 (was 0? No, assume init 0->0, 73->73).
            # So 0 holds 73, 73 holds 0.
            # Next op `CX 9 0`. (Physical 9, 0).
            # Logical at 9 is 9. Logical at 0 is 73.
            # Output `CX 9 73`.
            # This matches my previous intuition.
            
            # At the end, we have a permutation.
            # `logical_at_physical` tells us which logical qubit ended up at which physical wire in the ORIGINAL circuit.
            # In our OPTIMIZED circuit, logical qubit `L` is at physical `L`.
            # But the ORIGINAL circuit output `L` at `physical_where_L_ended_up`.
            # Wait. Stabilizers are checked on physical qubits.
            # If original circuit puts `L_5` at physical 5, we are good.
            # If original circuit puts `L_5` at physical 7, we must ensure our optimized circuit also puts `L_5` at physical 7.
            # Our optimized circuit (so far) leaves `L_5` at physical 5.
            # So we need to move `L_5` from 5 to 7.
            # So we need a final permutation layer.
            # Final map: `dest[p]` = `logical_at_physical[p]`.
            # This means "At physical p, we want logical `dest[p]`".
            # Currently at physical p, we have logical p.
            # So we want to permute: `p -> dest[p]`.
            # i.e., move contents of `p` to `find_idx(dest, p)`? No.
            # We have data `p` at `p`. We want `dest[p]` at `p`.
            # Example: `dest[0] = 73`. We want logical 73 at physical 0.
            # Currently logical 73 is at physical 73.
            # So we need to move 73 -> 0.
            # So we need to implement the permutation `P` where `P[i] = logical_at_physical[i]`.
            # i.e. we want `Physical[i]` to hold `Logical[logical_at_physical[i]]`.
            # Currently `Physical[i]` holds `Logical[i]`.
            # So we need to map `Logical[i] -> Logical[logical_at_physical[i]]` ?? No.
            # We want `Physical[i]` <-- `Logical[dest[i]]`.
            # We have `Physical[k]` == `Logical[k]`.
            # So we want to move data from `dest[i]` to `i`.
            # So permutation `pi` such that `pi(i) = dest[i]`.
            # We need to implement this permutation.
            
            # Let's verify with code.
            
            l_at_p = list(range(max_q + 1))
            
            # SWAP logic
            if is_swap: # Found SWAP(a, b)
                l_at_p[a], l_at_p[b] = l_at_p[b], l_at_p[a]
                # Skip 3 ops
            else:
                # Output gate
                if op[0] == "CX":
                    u, v = op[1], op[2]
                    lu, lv = l_at_p[u], l_at_p[v]
                    new_ops.append(("CX", lu, lv))
                elif op[0] == "H":
                    u = op[1]
                    lu = l_at_p[u]
                    new_ops.append(("H", lu))
                else:
                     # fallback
                    u = op[1]
                    lu = l_at_p[u]
                    new_ops.append((op[0], lu))
    
    # After loop, generate restoration swaps
    # We want final state at physical p to be logical `l_at_p[p]`.
    # Currently physical p holds logical p.
    # So we need to apply a permutation that moves data from `l_at_p[p]` to `p`.
    # Let `P[i] = l_at_p[i]`.
    # We want to move `P[i]` to `i`.
    # This is exactly the inverse of the permutation P?
    # If P says "at 0 is 73", we want to move 73 to 0.
    # Yes.
    
    # We can decompose this into SWAPs.
    # Cycle decomposition.
    
    return new_ops, l_at_p

def solve_permutation(perm):
    # perm[i] is the source: we want to move data from perm[i] to i.
    # Decompose into swaps.
    # Example: perm = [1, 0]. Move 1->0, 0->1. One swap (0, 1).
    # Example: perm = [1, 2, 0]. 
    # i=0: want from 1.
    # i=1: want from 2.
    # i=2: want from 0.
    # Cycle: 0 <- 1 <- 2 <- 0.
    # Swaps: (0, 1), then 0 has 1. 1 has 0.
    # Then (1, 2). 1 has 2. 2 has 0.
    # Result: 0 has 1, 1 has 2, 2 has 0. Correct.
    # So `(i, perm[i])`?
    # No, we need to be careful not to overwrite data we need later.
    
    swaps = []
    # visited array
    visited = [False] * len(perm)
    mapping = list(perm) # Copy
    
    # We want `mapping[i] == i` eventually? No.
    # We are generating swaps to transform the current state (where `Loc[x]=x`) 
    # to the target state (where `Loc[x]` matches `perm` logic).
    
    # Let's think:
    # Current state: `Val[i] = i`.
    # Target state: `Val[i] = perm[i]`.
    # We can apply swaps. `SWAP(a, b)` exchanges `Val[a]` and `Val[b]`.
    
    # Standard permutation decomposition.
    # Iterate i from 0 to N-1.
    # If `current_val[i] != target_val[i]`:
    #   Find `j` such that `current_val[j] == target_val[i]`.
    #   `SWAP(i, j)`.
    #   Now `current_val[i]` is correct.
    
    current_val = list(range(len(perm)))
    target_val = list(perm)
    
    for i in range(len(perm)):
        if current_val[i] != target_val[i]:
            # Find the element we want
            wanted = target_val[i]
            # Find where it is
            location = -1
            for k in range(i + 1, len(perm)):
                if current_val[k] == wanted:
                    location = k
                    break
            if location != -1:
                swaps.append((i, location))
                # Update current_val
                current_val[i], current_val[location] = current_val[location], current_val[i]
            else:
                # Should not happen if perm is valid
                pass
                
    return swaps

def run():
    baseline = stim.Circuit.from_file("baseline_task_v6.stim")
    print(f"Baseline CX: {count_cx(baseline)}")
    
    # Method 1: SWAP removal
    # Parse circuit
    # Re-implement the logic above
    ops = []
    for instr in baseline:
        if instr.name == "CX":
            targets = instr.targets_copy()
            for i in range(0, len(targets), 2):
                ops.append(("CX", targets[i].value, targets[i+1].value))
        elif instr.name == "H":
             for t in instr.targets_copy():
                ops.append(("H", t.value))
    
    # Determine max qubit
    max_q = 80
    
    # Optimization loop
    l_at_p = list(range(max_q + 1))
    new_ops = []
    
    i = 0
    removed_swaps = 0
    while i < len(ops):
        # Check for swap
        is_swap = False
        if i + 2 < len(ops):
            op1, op2, op3 = ops[i], ops[i+1], ops[i+2]
            if op1[0] == "CX" and op2[0] == "CX" and op3[0] == "CX":
                if op1[1] == op2[2] and op1[2] == op2[1] and op1[1] == op3[1] and op1[2] == op3[2]:
                     # Found SWAP(op1[1], op1[2])
                     u, v = op1[1], op1[2]
                     l_at_p[u], l_at_p[v] = l_at_p[v], l_at_p[u]
                     is_swap = True
                     removed_swaps += 1
                     i += 3
        
        if not is_swap:
            op = ops[i]
            if op[0] == "CX":
                u, v = op[1], op[2]
                new_ops.append(("CX", l_at_p[u], l_at_p[v]))
            elif op[0] == "H":
                u = op[1]
                new_ops.append(("H", l_at_p[u]))
            i += 1
            
    print(f"Removed {removed_swaps} internal SWAPs.")
    
    # Generate restoration swaps
    restoration_swaps = solve_permutation(l_at_p)
    print(f"Added {len(restoration_swaps)} restoration SWAPs.")
    
    # Build final circuit
    final_c = stim.Circuit()
    for op in new_ops:
        if op[0] == "CX":
            final_c.append("CX", [op[1], op[2]])
        elif op[0] == "H":
            final_c.append("H", [op[1]])
            
    # Add restoration swaps as 3 CXs
    for (u, v) in restoration_swaps:
        final_c.append("CX", [u, v])
        final_c.append("CX", [v, u])
        final_c.append("CX", [u, v])
        
    print(f"Candidate CX: {count_cx(final_c)}")
    
    # Verify candidate validity (stabilizers)
    # We can use Stim to verify if `final_c` has same tableau as `baseline`
    sim1 = stim.TableauSimulator()
    sim1.do_circuit(baseline)
    tab1 = sim1.current_inverse_tableau()
    
    sim2 = stim.TableauSimulator()
    sim2.do_circuit(final_c)
    tab2 = sim2.current_inverse_tableau()
    
    if tab1 == tab2:
        print("Tableaux match! Valid transformation.")
        # Check if better
        if count_cx(final_c) < count_cx(baseline):
             print("Improved CX count!")
             with open("candidate_circuit.stim", "w") as f:
                f.write(str(final_c).replace("CNOT", "CX"))
        else:
             print("CX count not improved.")

    # Method 2: Synthesis
    print("Attempting synthesis...")
    try:
        # Convert tableau to circuit
        # method="graph_state" is usually best for stabilizer states
        synth_c = tab1.to_circuit(method="graph_state")
        print(f"Graph State Synthesis CX: {count_cx(synth_c)}")
        
        if count_cx(synth_c) < count_cx(baseline):
            print("Synthesis is better!")
            # Verify just in case
            sim3 = stim.TableauSimulator()
            sim3.do_circuit(synth_c)
            tab3 = sim3.current_inverse_tableau()
            if tab3 == tab1:
                 with open("candidate_circuit.stim", "w") as f:
                    f.write(str(synth_c).replace("CNOT", "CX"))
            else:
                print("Synthesis tableau mismatch (unexpected).")
                
        synth_c2 = tab1.to_circuit(method="elimination")
        print(f"Elimination Synthesis CX: {count_cx(synth_c2)}")
         
        if count_cx(synth_c2) < count_cx(baseline):
            print("Elimination Synthesis is better!")
             # Verify
            sim4 = stim.TableauSimulator()
            sim4.do_circuit(synth_c2)
            tab4 = sim4.current_inverse_tableau()
            if tab4 == tab1:
                 with open("candidate_circuit.stim", "w") as f:
                    f.write(str(synth_c2).replace("CNOT", "CX"))
    except Exception as e:
        print(f"Synthesis failed: {e}")

    # Method 3: Synthesis from Stabilizers
    print("Attempting synthesis from stabilizers...")
    try:
        stabs = parse_stabilizers("stabilizers_task_v6.txt")
        # Note: allow_underconstrained=True is needed if N_stabs < N_qubits
        # Here 80 stabs for 81 qubits?
        tableau_s = stim.Tableau.from_stabilizers(stabs, allow_underconstrained=True)
        
        synth_s = tableau_s.to_circuit(method="graph_state")
        print(f"Stab Synthesis (Graph State) CX: {count_cx(synth_s)}")
        
        # Verify preservation
        sim_s = stim.TableauSimulator()
        sim_s.do_circuit(synth_s)
        preserved = 0
        for s in stabs:
             if sim_s.peek_observable_expectation(s) == 1:
                 preserved += 1
        print(f"Preserved {preserved}/{len(stabs)} stabilizers.")
        
        if preserved == len(stabs):
            if count_cx(synth_s) < count_cx(baseline):
                 print("Stab Synthesis is BETTER!")
                 with open("candidate_circuit.stim", "w") as f:
                    f.write(str(synth_s).replace("CNOT", "CX"))
            elif count_cx(synth_s) == count_cx(baseline):
                 # Check volume
                 if get_volume(synth_s) < get_volume(baseline):
                     print("Stab Synthesis is BETTER (volume)!")
                     with open("candidate_circuit.stim", "w") as f:
                        f.write(str(synth_s).replace("CNOT", "CX"))

        # Also try elimination
        synth_s2 = tableau_s.to_circuit(method="elimination")
        print(f"Stab Synthesis (Elimination) CX: {count_cx(synth_s2)}")
         
        # Verify
        sim_s2 = stim.TableauSimulator()
        sim_s2.do_circuit(synth_s2)
        preserved2 = 0
        for s in stabs:
             if sim_s2.peek_observable_expectation(s) == 1:
                 preserved2 += 1
        print(f"Preserved {preserved2}/{len(stabs)} stabilizers.")
        
        if preserved2 == len(stabs):
             if count_cx(synth_s2) < count_cx(baseline):
                 print("Stab Synthesis (Elim) is BETTER!")
                 with open("candidate_circuit.stim", "w") as f:
                    f.write(str(synth_s2).replace("CNOT", "CX"))
             elif count_cx(synth_s2) == count_cx(baseline):
                 if get_volume(synth_s2) < get_volume(baseline):
                     print("Stab Synthesis (Elim) is BETTER (volume)!")
                     with open("candidate_circuit.stim", "w") as f:
                        f.write(str(synth_s2).replace("CNOT", "CX"))

    except Exception as e:
        print(f"Stab Synthesis failed: {e}")


        # Check if tab2 preserves stabs
        # For each stab S, S' = tab2(S). Is S' == +S?
        # Actually `sim2.peek_observable_expectation(S)` should be +1.
        
        preserved = 0
        for s in stabs:
             if sim2.peek_observable_expectation(s) == 1:
                 preserved += 1
        print(f"Preserved {preserved}/{len(stabs)} stabilizers.")

if __name__ == "__main__":
    run()
