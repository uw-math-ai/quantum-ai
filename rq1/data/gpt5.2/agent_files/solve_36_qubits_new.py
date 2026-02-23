import stim

def solve():
    with open("stabilizers_36_new.txt", "r") as f:
        stabilizers = [line.strip() for line in f if line.strip()]

    print(f"Loaded {len(stabilizers)} stabilizers.")

    try:
        # Create a tableau from the stabilizers
        # allow_underconstrained=True lets us create a Tableau that satisfies these
        t = stim.Tableau.from_stabilizers(
            [stim.PauliString(s) for s in stabilizers],
            allow_redundant=True,
            allow_underconstrained=True
        )
        
        circuit = t.to_circuit("elimination")
        
        # Verify
        sim = stim.TableauSimulator()
        sim.do(circuit)
        
        all_good = True
        for i, s in enumerate(stabilizers):
            res = sim.peek_observable_expectation(stim.PauliString(s))
            if res != 1:
                print(f"Stabilizer {i} ({s}) failed (expectation {res})")
                all_good = False
        
        if all_good:
            print("All stabilizers verified successfully.")
            with open("circuit_36_new.stim", "w") as f:
                f.write(str(circuit))
            print("Circuit generated successfully.")
        else:
            print("Verification failed.")
            
    except Exception as e:
        print(f"Error generating circuit: {e}")

if __name__ == "__main__":
    solve()
