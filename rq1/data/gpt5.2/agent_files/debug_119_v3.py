import stim

def check():
    with open("stabilizers_119.txt", "r") as f:
        lines = [l.strip() for l in f if l.strip()]
    ps = [stim.PauliString(l) for l in lines]
    
    try:
        # Check if redundant
        t = stim.Tableau.from_stabilizers(ps, allow_redundant=False, allow_underconstrained=True)
        print("No redundant stabilizers found. They are independent.")
    except Exception as e:
        print(f"Redundant or inconsistent: {e}")
        
        # If redundant, let's try allow_redundant=True
        try:
            t = stim.Tableau.from_stabilizers(ps, allow_redundant=True, allow_underconstrained=True)
            print("Consistent (maybe redundant) with allow_underconstrained=True.")
            
            # Now verify if the tableau actually satisfies all input stabilizers
            # We can use tableau.measure_observable(p)
            # This returns result and modifies state if random.
            # But if the stabilizer is in the stabilizer group, it should be deterministic +1.
            # If it's deterministic -1, then it's inconsistent.
            
            sim = stim.TableauSimulator()
            sim.do(t.to_circuit())
            
            bad_indices = []
            for i, p in enumerate(ps):
                # Using peek_observable_expectation on simulator
                # Note: peek_observable_expectation returns expectation value.
                val = sim.peek_observable_expectation(p)
                if val != 1:
                    bad_indices.append(i)
                    if len(bad_indices) <= 5:
                        print(f"Stabilizer {i} expectation: {val}")
                        
            print(f"Total bad stabilizers: {len(bad_indices)}")
            
        except Exception as e2:
            print(f"Totally failed: {e2}")

if __name__ == "__main__":
    check()
