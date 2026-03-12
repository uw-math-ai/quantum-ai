import stim
import random
import time

def solve():
    print("Starting optimization...")
    try:
        with open("baseline.stim", "r") as f:
            baseline = stim.Circuit(f.read())
    except:
        print("Failed to read baseline.stim")
        return

    sim = stim.TableauSimulator()
    sim.do(baseline)
    # The tableau stabilizers
    # We want stabilizers of the final state (assuming input |0>).
    # If the circuit is unitary U, state is U|0>.
    # Stabilizers are S_i such that S_i |psi> = |psi>.
    # sim.current_stabilizers() gives these.
    original_stabilizers = sim.current_stabilizers()
    
    num_qubits = sim.num_qubits
    qubit_indices = list(range(num_qubits))
    
    best_vol = float('inf')
    best_circuit = None
    
    start_time = time.time()
    iterations = 0
    
    # Try identity first
    permutations_to_try = [list(range(num_qubits))]
    
    while time.time() - start_time < 20: # 20 seconds budget
        iterations += 1
        
        if iterations > 1:
            perm = list(range(num_qubits))
            random.shuffle(perm)
        else:
            perm = permutations_to_try[0]
            
        # Create inverse permutation map: old_index -> new_index
        # Actually, perm is a list where perm[i] is the new index for qubit i?
        # Let's define: P maps original qubit i to new qubit P[i].
        # So stabilizer on qubit i becomes stabilizer on P[i].
        
        # Mapping: old -> new
        old_to_new = {i: perm[i] for i in range(num_qubits)}
        # Mapping: new -> old (for relabeling back)
        new_to_old = {perm[i]: i for i in range(num_qubits)}
        
        # Permute stabilizers
        new_stabilizers = []
        for stab in original_stabilizers:
            # stab is stim.PauliString
            # We construct a new PauliString
            # P_new = I * (ops on new indices)
            
            # Efficient way:
            # Convert to x, z bits
            # x_old, z_old = stab.to_numpy() # (bool array)
            # x_new = x_old[inv_perm?] No.
            # If op at index i moves to index P[i], then new_op at k comes from old_op at P^-1[k].
            # So x_new[k] = x_old[new_to_old[k]]
            
            # Using python lists is fine for 100 qubits
            # stab[i] gives 0,1,2,3 for I,X,Y,Z
            
            new_vals = [0] * num_qubits
            for old_idx in range(num_qubits):
                # We need to handle if stabilizer length is less than num_qubits
                # stim.PauliString length is minimal.
                # But here stabilizers come from simulator so length is consistent?
                # Actually len(stab) might be less if trailing Is.
                val = 0
                if old_idx < len(stab):
                    val = stab[old_idx]
                
                new_idx = old_to_new[old_idx]
                if new_idx < num_qubits:
                    new_vals[new_idx] = val
            
            # Construct new PauliString
            # sign is preserved
            ps = stim.PauliString(new_vals)
            if stab.sign == -1:
                ps *= -1
            if stab.sign == 1j: # Should not happen for stabilizers
                ps *= 1j
            if stab.sign == -1j:
                ps *= -1j
                
            new_stabilizers.append(ps)
            
        # Synthesize
        try:
            # Use Tableau.from_stabilizers
            tableau = stim.Tableau.from_stabilizers(new_stabilizers, allow_redundant=True, allow_underconstrained=True)
            
            # Graph state synthesis
            circuit_perm = tableau.to_circuit(method="graph_state")
            
            # Relabel back to original qubits
            # If gate is on q_new, it should be on new_to_old[q_new]
            
            circuit_final = stim.Circuit()
            
            current_vol = 0
            has_measurements = False
            
            for instr in circuit_perm:
                if instr.name == "RX":
                    # Replace with H
                    targets = []
                    for t in instr.targets_copy():
                        q_new = t.value
                        q_old = new_to_old[q_new]
                        targets.append(q_old)
                        current_vol += 1 # H gate
                    circuit_final.append("H", targets)
                    
                elif instr.name == "CZ":
                    targets = []
                    for t in instr.targets_copy():
                        q_new = t.value
                        q_old = new_to_old[q_new]
                        targets.append(q_old)
                    circuit_final.append("CZ", targets)
                    # Volume for CZ is #pairs?
                    # stim instruction: CZ 0 1 2 3 -> pairs (0,1), (2,3)
                    # len(targets) is even. pairs = len/2.
                    # Wait, prompt said volume = total gate count in volume set.
                    # CZ is in volume set.
                    # Does CZ(0,1) count as 1 or 2?
                    # "cand.volume – total gate count in the volume gate set"
                    # Usually 2-qubit gate counts as 1 gate?
                    # Or maybe CZ decomposes?
                    # "CX, CY, CZ, H, S, SQRT_X, etc." are in the set.
                    # So 1 CZ is 1 volume.
                    # If instruction is CZ 0 1 2 3, it's 2 gates.
                    current_vol += len(targets) // 2
                    
                elif instr.name in ["TICK", "SHIFT_COORDS", "QUBIT_COORDS"]:
                    circuit_final.append(instr)
                elif instr.name in ["M", "MX", "MY", "MZ", "R", "RY", "RZ"]:
                     has_measurements = True
                     break
                else:
                    # Single qubit gates
                    targets = []
                    for t in instr.targets_copy():
                        if t.is_qubit_target:
                            q_new = t.value
                            q_old = new_to_old[q_new]
                            targets.append(q_old)
                            current_vol += 1
                        else:
                            targets.append(t)
                    circuit_final.append(instr.name, targets, instr.gate_args_copy())
            
            if has_measurements:
                continue
                
            # Check metrics
            if current_vol < best_vol:
                best_vol = current_vol
                best_circuit = circuit_final
                print(f"Iter {iterations}: New best volume {best_vol}")
                
        except Exception as e:
            # print(f"Error in iter {iterations}: {e}")
            pass
            
    if best_circuit:
        with open("candidate.stim", "w") as f:
            f.write(str(best_circuit))
        print("Done. Best candidate written.")
    else:
        print("No valid candidate found.")

if __name__ == "__main__":
    solve()
