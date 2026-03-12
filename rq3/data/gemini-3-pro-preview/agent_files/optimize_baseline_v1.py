import stim

baseline_str = """
CX 58 0 0 58 58 0
H 0 8 11 13 56
CX 0 8 0 11 0 13 0 14 0 21 0 56 0 61 0 62
H 7 58
CX 7 0 58 0 14 1 1 14 14 1 7 1 58 1 21 2 2 21 21 2 7 2 58 2 58 3 3 58 58 3 3 28 3 35 28 4 4 28 28 4 35 5 5 35 35 5 42 6 6 42 42 6 6 49 6 61 7 6 7 49 49 8 8 49 49 8 49 9 9 49 49 9 9 15 9 22 9 60 9 61
H 14 57
CX 14 9 57 9 15 10 10 15 15 10 14 10 57 10 22 11 11 22 22 11 14 11 57 11 14 12 12 14 14 12 12 29 12 36 29 13 13 29 29 13 36 14 14 36 36 14 61 15 15 61 61 15 15 43 15 50 15 60 47 15 43 16 16 43 43 16 47 16 50 17 17 50 50 17 47 17 56 18 18 56 56 18
H 61
CX 18 22 18 23 18 43 18 57 18 59 18 60 18 61
H 21 49
CX 21 18 49 18 43 19 19 43 43 19 21 19 49 19 23 20 20 23 23 20 21 20 49 20 21 30 21 37 30 22 22 30 30 22 37 23 23 37 37 23 49 24 24 49 49 24 24 44 24 51 44 25 25 44 44 25 51 26 26 51 51 26 61 27 27 61 61 27 27 49 27 50 27 60
H 58
CX 57 27 58 27 50 28 28 50 50 28 57 28 58 28 49 29 29 49 49 29 57 29 58 29 58 30 30 58 58 30 30 31 30 38 38 32 32 38 38 32 60 33 33 60 60 33 33 45 33 52 55 33 62 33 45 34 34 45 45 34 55 34 62 34 52 35 35 52 52 35 55 35 62 35 58 36 36 58 58 36 36 44 36 56 36 59
H 50
CX 50 36 56 37 37 56 56 37 50 37 44 38 38 44 44 38 50 38 50 39 39 50 50 39 39 44 39 50 44 40 40 44 44 40 50 41 41 50 50 41 59 42 42 59 59 42 42 46 42 53 47 42 55 42 62 42 46 43 43 46 46 43 47 43 55 43 62 43 53 44 44 53 53 44 47 44 55 44 62 44 57 45 45 57 57 45 45 46 45 49 45 51 45 62
H 52 58
CX 52 45 58 45 52 46 58 46 51 47 47 51 51 47 52 47 58 47 52 48 48 52 52 48 48 53 48 60 60 49 49 60 60 49 53 50 50 53 53 50 51 54 58 51 58 52 52 58 58 52 52 54 54 53 53 54 54 53 60 54 54 60 60 54 54 56 54 61 54 62
H 59
CX 59 54 56 55 55 56 56 55 59 55 61 56 56 61 61 56 59 56 59 57 57 59 59 57 57 59 57 60 59 58 58 59 59 58 60 59 59 60 60 59 61 60 60 61 61 60 60 61 62 60 62 61
"""

try:
    baseline = stim.Circuit(baseline_str)
    
    # Simulate to get the final tableau
    sim = stim.TableauSimulator()
    sim.do(baseline)
    # The current state is the result of applying baseline to |0...0>
    # We want a circuit that prepares this state.
    # Inverse of current tableau maps current state back to |0...0>.
    # So we want the inverse of the inverse, which is the current tableau itself, applied to |0...0>.
    # Stim's tableau representation is tricky.
    # sim.current_inverse_tableau().inverse() gives the tableau of the operation performed so far.
    # If the operation is unitary U, this gives U.
    # We want a circuit for U.
    
    tableau = sim.current_inverse_tableau().inverse()
    
    # Generate graph state circuit
    # This method attempts to synthesize a circuit using graph state preparation logic
    # It typically uses H, S, CZ, and single qubit Cliffords.
    candidate = tableau.to_circuit(method="graph_state")
    
    # Graph state synthesis often includes 'RX' gates to reset qubits if it assumes arbitrary input state.
    # However, since we are preparing a stabilizer state from |0...0> (implicitly),
    # any 'RX' gate (Reset X) is effectively preparing |+>.
    # So we can replace 'RX' with 'H' (since H|0> = |+>) and 'R' with nothing (since |0> is already |0>).
    # But wait, to_circuit output assumes it's implementing the tableau operation.
    # If the tableau operation includes initialization, it might use resets.
    
    # Let's inspect the candidate for resets.
    # We can iterate and replace.
    
    new_cand = stim.Circuit()
    for instr in candidate:
        if instr.name == "RX":
            # RX resets the qubit to |+>. Since we start at |0>, H does this.
            # But wait, this is only valid if the qubit hasn't been used yet or we don't care about previous state.
            # Since this is a full state preparation circuit usually, resets at the beginning are fine.
            # But if resets appear later, it might be tricky.
            # However, standard graph state usually starts with H on all qubits in the graph, then CZs.
            # So RX at the start is just H.
            targets = instr.targets_copy()
            new_cand.append("H", targets)
        elif instr.name == "R" or instr.name == "RZ":
            # R or RZ resets to |0>. Since we start at |0>, this is a no-op if at the beginning.
            # If in the middle, it's a reset.
            # But graph state logic usually doesn't reset in the middle for pure stabilizer states.
            # Let's assume these are initializations.
            pass
        elif instr.name == "MY" or instr.name == "MR" or instr.name == "M":
             # Measurement is not allowed unless in baseline (baseline has none).
             # If graph state introduces them, that's bad.
             # But for pure stabilizer state, it shouldn't.
             new_cand.append(instr)
        else:
            new_cand.append(instr)
            
    with open("candidate.stim", "w") as f:
        print(new_cand, file=f)
    print("Candidate written to candidate.stim")

except Exception as e:
    print(f"Error: {e}")
