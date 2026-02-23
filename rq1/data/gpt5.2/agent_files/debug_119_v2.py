import stim

def check_consistency():
    with open("stabilizers_119.txt", "r") as f:
        lines = [l.strip() for l in f if l.strip()]
    
    ps = [stim.PauliString(l) for l in lines]
    
    # Check consistency by adding them one by one to a TableauSimulator?
    # Or just use Tableau.from_stabilizers without allow_redundant
    try:
        t = stim.Tableau.from_stabilizers(ps)
        print("Consistent and independent.")
    except Exception as e:
        print(f"Not consistent or not independent: {e}")
        
    # Try with allow_redundant
    try:
        t = stim.Tableau.from_stabilizers(ps, allow_redundant=True)
        print("Consistent with allow_redundant=True.")
        
        # Now verify if the tableau actually satisfies all input stabilizers
        # The tableau defines a state. Let's check the expectation values.
        # We can simulate the circuit and measure the stabilizers.
        circuit = t.to_circuit()
        sim = stim.TableauSimulator()
        sim.do(circuit)
        
        failures = []
        for i, p in enumerate(ps):
            # measure_expectation returns +1, -1, or 0
            # Since it's a stabilizer state, it should be +1 or -1 (if in group) or 0 (if not in group)
            # Actually, measure_expectation gives expectation value.
            # But we can just use peek_observable_expectation
            
            # Wait, peek_observable_expectation is not available in stim python?
            # We can use `canonical_stabilizers` of the tableau to check.
            pass
            
            # Better: use measure_pauli_string
            # But that collapses the state if result is random.
            # We want to check if it's deterministic +1.
            
            res = sim.measure_observable(p)
            # But this modifies state if random.
            # We can use peek_bloch on each qubit but that's local.
            
            # Let's just use the tableau methods.
            # x_output, z_output.
            pass
            
    except Exception as e:
        print(f"Inconsistent even with allow_redundant=True? {e}")

if __name__ == "__main__":
    check_consistency()
