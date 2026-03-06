import stim

def debug():
    try:
        with open("stabilizers_135.txt", "r") as f:
            lines = [l.strip() for l in f if l.strip()]
        
        stabs = [stim.PauliString(l) for l in lines]
        print(f"Loaded {len(stabs)} stabilizers.")

        # Check commutativity
        for i in range(len(stabs)):
            for j in range(i + 1, len(stabs)):
                if not stabs[i].commutes(stabs[j]):
                    print(f"Stabilizers {i} and {j} anti-commute!")
                    print(f"{stabs[i]}")
                    print(f"{stabs[j]}")
                    return

        print("All stabilizers commute.")

        # Create tableau with allow_redundant
        t = stim.Tableau.from_stabilizers(stabs, allow_underconstrained=True, allow_redundant=True)
        print("Tableau created successfully with redundant stabilizers.")
        
        # Generate circuit
        circuit = t.to_circuit("elimination")
        
        # Simulate
        sim = stim.TableauSimulator()
        sim.do_circuit(circuit)
        
        preserved_count = 0
        failed_indices = []
        for i, s in enumerate(stabs):
            exp = sim.peek_observable_expectation(s)
            if exp == 1:
                preserved_count += 1
            else:
                failed_indices.append(i)
        
        print(f"Simulation preserves {preserved_count}/{len(stabs)} stabilizers.")
        if failed_indices:
            print(f"First 5 failed indices: {failed_indices[:5]}")
            print(f"First failed stabilizer: {stabs[failed_indices[0]]}")
            print(f"Expectation: {sim.peek_observable_expectation(stabs[failed_indices[0]])}")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    debug()
