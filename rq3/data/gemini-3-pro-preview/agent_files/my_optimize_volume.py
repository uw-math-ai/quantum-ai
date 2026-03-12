import stim
import random
import sys

# The baseline string from the prompt
baseline_str = """
H 0
CX 0 24 0 32 0 49
H 8 48
CX 8 0 48 0 49 1 1 49 49 1 1 24 25 1 33 1 34 1 37 1 38 1 39 1 41 1 45 1 46 1 47 1 48 1 50 1 51 1 52 1 53 1 54 1 55 1 8 2 2 8 8 2 2 24 48 2 16 3 3 16 16 3
H 3
CX 3 40 24 4 4 24 24 4 4 32 4 40 25 4 32 4 33 4 34 4 37 4 38 4 39 4 40 4 41 4 45 4 46 4 47 4 50 4 51 4 52 4 53 4 54 4 55 4 32 5 5 32 32 5 40 5 40 6 6 40 40 6 25 6 33 6 34 6 37 6 38 6 39 6 41 6 45 6 46 6 47 6 50 6 51 6 52 6 53 6 54 6 55 6 49 7 7 49 49 7
H 7 17
CX 7 17 7 25 7 33 7 50
H 9
CX 9 7 48 7 25 8 8 25 25 8 33 8 41 8 48 8 50 8 9 17 9 50 48 9 50 10 10 50 50 10 10 41 17 10 17 11 11 17 17 11 11 33 41 12 12 41 41 12 33 12 33 13 13 33 33 13 50 14 14 50 50 14
H 14 18
CX 14 18 14 26 14 34
H 25
CX 25 14 48 14 25 15 15 25 25 15 15 18 15 34 15 53 48 15 34 16 16 34 34 16 48 16 53 16 42 17 17 42 42 17 18 17 26 17 53 17 18 26 18 53 26 19 19 26 26 19 53 20 20 53 53 20 42 21 21 42 42 21
H 21
CX 21 27 21 35 21 52
H 34
CX 34 21 48 21 34 22 22 34 34 22 22 35 48 22 52 23 23 52 52 23 23 35 48 23 26 24 24 26 26 24
H 24
CX 24 43 27 25 25 27 27 25 25 35 25 43 35 25 43 25 35 26 26 35 35 26 43 26 43 27 27 43 43 27 35 28 28 35 35 28
H 28 32 40 41 49
CX 28 32 28 35 28 36 28 40 28 41 28 48 28 49 28 51 28 54 28 55 41 28 48 28 48 29 29 48 48 29 29 32 29 35 29 40 29 41 29 49 29 51 29 54 29 55 41 30 30 41 41 30 30 35 53 31 31 53 53 31
H 31
CX 31 44 35 32 32 35 35 32 32 36 32 44 36 32 44 32 36 33 33 36 36 33 44 33 44 34 34 44 44 34 36 35 35 36 36 35
H 35
CX 35 37 35 48 36 35 36 37 36 51 45 37 51 37 42 38 38 42 42 38
H 38
CX 38 45 38 51 48 39 39 48 48 39 39 45 51 39 51 40 40 51 51 40 45 41 41 45 45 41 50 42 42 50 50 42
H 42
CX 42 45 42 50 51 42 51 43 43 51 51 43 43 50 43 55 50 44 44 50 50 44 46 44 55 44 50 45 45 50 50 45
H 45
CX 45 46 45 55 50 46 46 50 50 46 46 50 55 46 55 47 47 55 55 47 50 48 48 50 50 48 51 49 49 51 51 49
H 49
CX 49 50 49 53 51 49 51 50 50 51 51 50 50 51 50 54 54 51 55 51
H 52
CX 52 54 52 55 53 55 54 53
"""

def count_volume(circuit):
    vol = 0
    for instr in circuit:
        name = instr.name
        targets = instr.targets_copy()
        if name == "CZ":
            vol += len(targets) // 2
        elif name in ["H", "S", "X", "Y", "Z", "RX", "RY", "RZ"]:
            vol += len(targets)
        elif name == "TICK":
            pass
        else:
            vol += len(targets)
    return vol

def solve():
    print("Parsing baseline...")
    baseline = stim.Circuit(baseline_str)
    sim = stim.TableauSimulator()
    sim.do(baseline)
    tableau = sim.current_inverse_tableau().inverse()
    n_qubits = len(tableau)
    print(f"Qubits: {n_qubits}")
    
    stabs = tableau.to_stabilizers()
    
    best_vol = float('inf')
    best_circuit_str = ""
    
    # Generate 100 permutations
    perms = [list(range(n_qubits))]
    for _ in range(99):
        p = list(range(n_qubits))
        random.shuffle(p)
        perms.append(p)
        
    print(f"Searching {len(perms)} permutations...")
    
    for i, perm in enumerate(perms):
        # Inverse permutation
        inv_perm = [0] * n_qubits
        for old, new in enumerate(perm):
            inv_perm[new] = old
            
        new_stabs = []
        for s in stabs:
            # Manually construct new PauliString
            # p_new[perm[k]] = p_old[k]
            new_s_vals = [0] * n_qubits
            # s is a PauliString
            # In stim 1.12+, s can be iterated or accessed
            # But let's use the string representation as it's easiest to manipulate if we don't want to rely on specific version API
            # s.to_numpy()?
            # Let's use string repr
            # s is stim.PauliString
            
            # Efficient access:
            for k in range(n_qubits):
                # stim.PauliString index access returns 0,1,2,3
                op = s[k]
                if op != 0:
                    new_s_vals[perm[k]] = op
            
            # Reconstruct
            new_s = stim.PauliString(new_s_vals)
            new_stabs.append(new_s)
            
        try:
            # Synthesize
            t_new = stim.Tableau.from_stabilizers(new_stabs, allow_redundant=True)
            c_new = t_new.to_circuit(method="graph_state")
            
            # Remap circuit
            c_remapped = stim.Circuit()
            for instr in c_new:
                name = instr.name
                targets = instr.targets_copy()
                new_targets = []
                for t in targets:
                    if t.is_qubit_target:
                        new_targets.append(inv_perm[t.value])
                    else:
                        new_targets.append(t.value)
                c_remapped.append(name, new_targets)
            
            vol = count_volume(c_remapped)
            
            if vol < best_vol:
                best_vol = vol
                best_circuit_str = str(c_remapped)
                print(f"Iter {i}: Found better volume {vol}")
                
        except Exception as e:
            # print(f"Iter {i} failed: {e}")
            pass

    # Fix RX -> H
    # The string might be "RX 0 1 2..."
    # We replace RX with H
    # But wait, RX resets to X. H on 0 maps Z->X.
    # If the input is |0>, H makes |+>. RX makes |+>. Equivalent.
    # If the input is NOT |0>, RX resets it. H does not.
    # The prompt says "Do NOT introduce measurements, resets, or noise unless they already exist in the baseline".
    # Baseline has no resets.
    # So we MUST NOT use RX.
    # Using H instead of RX is correct assumption that input is |0>.
    
    final_str = best_circuit_str.replace("RX", "H")
    
    with open("candidate_opt.stim", "w") as f:
        f.write(final_str)
    print("Saved candidate_opt.stim")

if __name__ == "__main__":
    solve()
