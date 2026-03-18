import stim

baseline_str = """
CX 1 0 0 1 1 0
H 0
CX 0 3 0 4
H 1
CX 1 0 1 4 1 6 4 2 2 4 4 2 5 2 6 2 4 3 3 4 4 3
H 3
CX 3 5 3 6 4 5 6 4 6 5 5 6 6 5
"""

target_stabilizers_str = [
    "XXIIXXI", "XIXIXIX", "IIIXXXX",
    "ZZIIZZI", "ZIZIZIZ", "IIIZZZZ"
]

def check_state_prep(circuit, stabilizers):
    sim = stim.TableauSimulator()
    sim.do(circuit)
    
    # Check if the output state is stabilized by each stabilizer
    for s_str in stabilizers:
        p = stim.PauliString(s_str)
        if not sim.measure_observable(p) == 0:
            # Measure observable returns a random result if not determined, 
            # or the deterministic result.
            # Ideally we check expectation value.
            # peek_observable_expectation returns +1, -1, or 0 (uncertain).
            exp = sim.peek_observable_expectation(p)
            if exp != 1:
                return False
    return True

def check_preservation(circuit, stabilizers):
    # Check if U * S * U^dagger = S
    # We can use Tableau.
    t = circuit.to_tableau()
    
    for s_str in stabilizers:
        p = stim.PauliString(s_str)
        # Apply U P U^dagger
        # In Stim tableau, t(P) gives U P U^dagger (or inverse? check docs)
        # t(P) is the result of conjugating P by the circuit.
        # Actually t.call(P) or similar.
        # t(PauliString) returns the conjugated PauliString.
        mapped = t(p)
        if mapped != p:
            return False
    return True

circuit = stim.Circuit(baseline_str)

print("Checking State Prep (Input |0>):")
is_state_prep = check_state_prep(circuit, target_stabilizers_str)
print(f"Is State Prep: {is_state_prep}")

print("Checking Stabilizer Preservation (Commutation):")
is_preserving = check_preservation(circuit, target_stabilizers_str)
print(f"Is Preserving: {is_preserving}")
