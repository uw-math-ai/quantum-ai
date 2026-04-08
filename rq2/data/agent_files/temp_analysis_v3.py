import stim
import sys

def analyze():
    # Load circuit and stabilizers
    circuit_str = """H 0 2 4 6 9 11 13 16 18 20 43\nCX 0 2 0 4 0 6 0 9 0 11 0 13 0 16 0 18 0 20 0 21 0 28 0 43\nH 7\nCX 7 0 43 1 1 43 43 1\nH 14\nCX 1 2 1 4 1 6 1 9 1 11 1 13 1 14 1 16 1 18 1 20 1 21 1 45 1 46\nH 42\nCX 42 1 14 2 2 14 14 2 2 21 2 28 2 35 2 45 2 46 7 2 42 2 21 3 3 21 21 3 3 35 28 4 4 28 28 4 4 35 4 45 4 46 7 4 42 4 35 5 5 35 35 5 7 6 6 7 7 6 43 7 7 43 43 7\nH 7 12 19 35\nCX 7 11 7 12 7 18 7 19 7 22 7 28 7 29 7 35 7 42 7 45 7 46 7 48\nH 8\nCX 8 7 42 8 8 42 42 8\nH 15\nCX 8 11 8 12 8 15 8 18 8 19 8 22 8 28 8 35 8 46 8 48 15 9 9 15 15 9 9 22 9 29 9 36 9 45 42 9 22 10 10 22 22 10 10 36 29 11 11 29 29 11 11 36 11 45 42 11 36 12 12 36 36 12 42 13 13 42 42 13 15 14 14 15 15 14 14 16 14 23 14 30 15 14 15 16 15 30 15 46 16 23 16 30 16 37 16 46 23 17 17 23 23 17 17 37 46 18 18 46 46 18 18 30 18 37 31 18 33 18 47 18 48 18 37 19 19 37 37 19 31 19 33 19 47 19 48 19 30 20 20 30 30 20 31 20 33 20 47 20 48 20\nH 21 44\nCX 21 24 21 28 21 29 21 30 21 31 21 35 21 36 21 37 21 42 21 43 21 44 21 46 21 48\nH 22\nCX 22 21 44 22 22 44 44 22\nH 23\nCX 22 23 22 24 22 28 22 29 22 30 22 35 22 36 22 37 22 42 22 43 22 46 22 47 22 48 23 24 23 31 23 38 23 47 44 23 24 38 31 25 25 31 31 25 25 38 25 47 44 25 38 26 26 38 38 26 44 27 27 44 44 27 29 28 28 29 29 28 28 31 28 32 28 46 29 28 29 32 29 45 29 46 29 47 46 30 30 46 46 30 30 31 30 32 30 39 30 45 30 47 31 39 45 32 32 45 45 32 32 39 32 45 32 47 33 32 48 32 39 33 33 39 39 33 39 33 48 33 45 34 34 45 45 34 39 34 48 34 36 35 35 36 36 35 35 37 35 38 35 39 35 48 36 35 36 37 36 39 37 38 37 39 37 40 38 40 39 40 48 39 48 40 48 41 41 48 48 41 42 44 42 45 42 46 43 42 43 45 43 46 43 47 46 44 44 46 46 44 44 45 44 46 44 47 44 48 46 45 45 46 46 45 45 48 47 46 46 47 47 46 46 47 46 48 48 47 47 48 48 47"""
    
    stabilizers_str = """XXXXIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIII, IIIIIIIXXXXIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIII, IIIIIIIIIIIIIIXXXXIIIIIIIIIIIIIIIIIIIIIIIIIIIIIII, IIIIIIIIIIIIIIIIIIIIIXXXXIIIIIIIIIIIIIIIIIIIIIIII, IIIIIIIIIIIIIIIIIIIIIIIIIIIIXXXXIIIIIIIIIIIIIIIII, IIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIXXXXIIIIIIIIII, IIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIXXXXIII, XIXIXIXIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIII, IIIIIIIXIXIXIXIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIII, IIIIIIIIIIIIIIXIXIXIXIIIIIIIIIIIIIIIIIIIIIIIIIIII, IIIIIIIIIIIIIIIIIIIIIXIXIXIXIIIIIIIIIIIIIIIIIIIII, IIIIIIIIIIIIIIIIIIIIIIIIIIIIXIXIXIXIIIIIIIIIIIIII, IIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIXIXIXIXIIIIIII, IIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIXIXIXIX, IIXXXXIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIII, IIIIIIIIIXXXXIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIII, IIIIIIIIIIIIIIIIXXXXIIIIIIIIIIIIIIIIIIIIIIIIIIIII, IIIIIIIIIIIIIIIIIIIIIIIXXXXIIIIIIIIIIIIIIIIIIIIII, IIIIIIIIIIIIIIIIIIIIIIIIIIIIIIXXXXIIIIIIIIIIIIIII, IIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIXXXXIIIIIIII, IIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIXXXXI, ZZZZIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIII, IIIIIIIZZZZIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIII, IIIIIIIIIIIIIIZZZZIIIIIIIIIIIIIIIIIIIIIIIIIIIIIII, IIIIIIIIIIIIIIIIIIIIIZZZZIIIIIIIIIIIIIIIIIIIIIIII, IIIIIIIIIIIIIIIIIIIIIIIIIIIIZZZZIIIIIIIIIIIIIIIII, IIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIZZZZIIIIIIIIII, IIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIZZZZIII, ZIZIZIZIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIII, IIIIIIIZIZIZIZIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIII, IIIIIIIIIIIIIIZIZIZIZIIIIIIIIIIIIIIIIIIIIIIIIIIII, IIIIIIIIIIIIIIIIIIIIIZIZIZIZIIIIIIIIIIIIIIIIIIIII, IIIIIIIIIIIIIIIIIIIIIIIIIIIIZIZIZIZIIIIIIIIIIIIII, IIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIZIZIZIZIIIIIII, IIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIZIZIZIZ, IIZZZZIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIII, IIIIIIIIIZZZZIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIII, IIIIIIIIIIIIIIIIZZZZIIIIIIIIIIIIIIIIIIIIIIIIIIIII, IIIIIIIIIIIIIIIIIIIIIIIZZZZIIIIIIIIIIIIIIIIIIIIII, IIIIIIIIIIIIIIIIIIIIIIIIIIIIIIZZZZIIIIIIIIIIIIIII, IIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIZZZZIIIIIIII, IIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIZZZZI, IXXIXIIIXXIXIIIIIIIIIIIIIIIIIXXIXIIIXXIXIIIIIIIII, IXXIXIIIIIIIIIIXXIXIIIIIIIIIIXXIXIIIIIIIIIIXXIXII, IIIIIIIIIIIIIIIIIIIIIIXXIXIIIXXIXIIIXXIXIIIXXIXII, IZZIZIIIZZIZIIIIIIIIIIIIIIIIIZZIZIIIZZIZIIIIIIIII, IZZIZIIIIIIIIIIZZIZIIIIIIIIIIZZIZIIIIIIIIIIZZIZII, IIIIIIIIIIIIIIIIIIIIIIZZIZIIIZZIZIIIZZIZIIIZZIZII"""
    
    stabilizers = [s.strip() for s in stabilizers_str.split(',')]
    stim_stabilizers = [stim.PauliString(s) for s in stabilizers]
    
    circuit = stim.Circuit(circuit_str)
    
    ops = []
    for instr in circuit:
        if instr.name in ["CX", "H", "S", "X", "Y", "Z", "I", "SWAP", "CZ"]:
             targets = instr.targets_copy()
             arity = 2 if instr.name in ["CX", "SWAP", "CZ"] else 1
             if arity == 2:
                 for k in range(0, len(targets), 2):
                     ops.append((instr.name, [t.value for t in targets[k:k+2]]))
             else:
                 for t in targets:
                     ops.append((instr.name, [t.value]))
    
    print(f"Scanning {len(ops)} operations...")
    
    failures = []
    
    for i in range(len(ops) + 1):
        if i % 100 == 0: print(f"  Op {i}...")
        
        # Build suffix for this op
        # We need the tableau that represents ops[i:].
        suffix_circuit = stim.Circuit()
        for k in range(i, len(ops)):
             op, targs = ops[k]
             suffix_circuit.append(op, targs)
        
        t_suffix = stim.Tableau.from_circuit(suffix_circuit)
        
        for q in range(49):
            for p_char in ["X", "Z", "Y"]:
                p = stim.PauliString(49)
                if p_char == "X": p[q] = 1
                elif p_char == "Z": p[q] = 2
                elif p_char == "Y": p[q] = 3
                
                # Propagate
                e_final = t_suffix(p)
                
                # Check weight
                w = sum(1 for k in range(49) if e_final[k] != 0)
                
                if w > 4:
                    # Check if it stabilizes the ideal state?
                    # We need the ideal state.
                    # We can get it by running the circuit without faults.
                    # But we need to do this once.
                    pass
                    
                    commutes = True
                    for s in stim_stabilizers:
                        if not e_final.commutes(s):
                            commutes = False
                            break
                    if commutes:
                        # It commutes with all stabilizers.
                        # Check if it is a stabilizer (expectation +1).
                        # We need a simulator with the state.
                        # Re-run simulation to get expectation.
                        
                        # Note: This is slow to do for every fault.
                        # But we only do it for the fails.
                        
                        sim_verify = stim.TableauSimulator()
                        sim_verify.do(circuit)
                        exp = sim_verify.peek_observable_expectation(e_final)
                        
                        if exp == 1:
                            # It is a stabilizer. Harmless.
                            continue
                        elif exp == -1:
                            msg = f"FAIL: Op {i} Q{q} {p_char} -> Weight {w} (Logical Phase Error?)"
                        else:
                            # Expectation 0? Impossible if commutes with all stabilizers.
                            msg = f"FAIL: Op {i} Q{q} {p_char} -> Weight {w} (Undetected)"
                            
                        failures.append(msg)
                        if len(failures) < 5:
                            print(msg)
                        elif len(failures) == 5:
                            print("... and more ...")
                            return

    if not failures:
        print("SUCCESS: No undetected high-weight errors found!")
    else:
        print(f"FAILED: Found {len(failures)} undetected high-weight errors.")

    # Check canonical stabilizers
    sim = stim.TableauSimulator()
    sim.do(circuit)
    canon = sim.canonical_stabilizers()
    print(f"Canonical stabilizers count: {len(canon)}")
    
    # Check if Q48 X commutes with canon
    # Use one of the failure examples
    # Op 0 Q48 X
    # Propagate it
    # We need to propagate X on 48 through the whole circuit.
    # We can use Tableau of circuit.
    t_total = stim.Tableau.from_circuit(circuit)
    p = stim.PauliString(49)
    p[48] = 1 # X
    e_final = t_total(p)
    
    # Check commutation with canon
    commutes_canon = True
    for s in canon:
        if not e_final.commutes(s):
            commutes_canon = False
            break
    print(f"Q48 X commutes with canonical stabs: {commutes_canon}")
    
    # Check expectation with canon
    # exp = sim.peek_observable_expectation(e_final) # We did this, it was 0?
    # Actually, in the loop we used sim_verify which did do(circuit).
    # So expectation 0 implies it is NOT a stabilizer.

if __name__ == "__main__":
    analyze()
