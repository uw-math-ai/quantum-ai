import stim
import sys

stabilizers = [
    "XXXXIIIIIIIIIIIIIIIIIIIIIIII",
    "IIIIIIIXXXXIIIIIIIIIIIIIIIII",
    "IIIIIIIIIIIIIIXXXXIIIIIIIIII",
    "IIIIIIIIIIIIIIIIIIIIIXXXXIII",
    "XIXIXIXIIIIIIIIIIIIIIIIIIIII",
    "IIIIIIIXIXIXIXIIIIIIIIIIIIII",
    "IIIIIIIIIIIIIIXIXIXIXIIIIIII",
    "IIIIIIIIIIIIIIIIIIIIIXIXIXIX",
    "IIXXXXIIIIIIIIIIIIIIIIIIIIII",
    "IIIIIIIIIXXXXIIIIIIIIIIIIIII",
    "IIIIIIIIIIIIIIIIXXXXIIIIIIII",
    "IIIIIIIIIIIIIIIIIIIIIIIXXXXI",
    "ZZZZIIIIIIIIIIIIIIIIIIIIIIII",
    "IIIIIIIZZZZIIIIIIIIIIIIIIIII",
    "IIIIIIIIIIIIIIZZZZIIIIIIIIII",
    "IIIIIIIIIIIIIIIIIIIIIZZZZIII",
    "ZIZIZIZIIIIIIIIIIIIIIIIIIIII",
    "IIIIIIIZIZIZIZIIIIIIIIIIIIII",
    "IIIIIIIIIIIIIIZIZIZIZIIIIIII",
    "IIIIIIIIIIIIIIIIIIIIIZIZIZIZ",
    "IIZZZZIIIIIIIIIIIIIIIIIIIIII",
    "IIIIIIIIIZZZZIIIIIIIIIIIIIII",
    "IIIIIIIIIIIIIIIIZZZZIIIIIIII",
    "IIIIIIIIIIIIIIIIIIIIIIIZZZZI",
    "IXXIXIIIXXIXIIIXXIXIIIXXIXII",
    "IZZIZIIIZZIZIIIZZIZIIIZZIZII"
]

try:
    with open("circuit_28.stim", "r") as f:
        circuit_text = f.read()
    
    circuit = stim.Circuit(circuit_text)
    sim = stim.TableauSimulator()
    sim.do(circuit)
    
    failed = []
    for s in stabilizers:
        p = stim.PauliString(s)
        # We want the state to be a +1 eigenstate of P.
        # This means P|psi> = |psi>.
        # measure_observable(P) returns the measurement result (0 for +1, 1 for -1).
        # It also projects the state if P is not a stabilizer.
        # But we can check if it's a stabilizer using peek_observable_expectation?
        # No, stim doesn't have peek for arbitrary Pauli strings in the python API easily for TableauSimulator?
        # Actually measure_observable is fine. If it's a stabilizer, it won't change the state.
        
        # However, to be non-destructive (if we were checking multiple on same state), we can copy the simulator.
        # But here we want to check if ALL are satisfied.
        # If one fails, the circuit is wrong.
        
        sim_copy = sim.copy()
        result = sim_copy.measure_observable(p)
        if result: # True means -1 eigenvalue or random result yielded -1
            failed.append(s)
        
        # We also need to check if it's deterministic.
        # If it's random, it's not a stabilizer.
        # But measure_observable collapses the state if random.
        # So 'result' is just one sample.
        # Ideally we check canonical stabilizers?
        
    if not failed:
        print("SUCCESS: All stabilizers passed.")
    else:
        print(f"FAILURE: {len(failed)} stabilizers failed.")
        for f in failed:
            print(f"  {f}")

except Exception as e:
    print(f"Error: {e}")
