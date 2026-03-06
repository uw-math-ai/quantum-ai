import stim
import sys

def solve():
    # Read stabilizers
    try:
        with open(r'C:\Users\anpaz\Repos\quantum-ai\rq1\stabilizers_85.txt', 'r') as f:
            lines = [l.strip() for l in f if l.strip()]
    except Exception as e:
        print(f"Error reading file: {e}")
        return
    
    print(f"Read {len(lines)} stabilizers")
    
    # Check length
    for line in lines:
        if len(line) != 85:
            print(f"Error: Stabilizer length is {len(line)}, expected 85")
            return

    # Convert to Stim PauliStrings
    try:
        stabilizers = [stim.PauliString(s) for s in lines]
    except Exception as e:
        print(f"Error parsing stabilizers: {e}")
        return

    # Check for commutativity
    print("Checking commutativity...")
    anticommuting_pairs = []
    for i in range(len(stabilizers)):
        for j in range(i + 1, len(stabilizers)):
            if not stabilizers[i].commutes(stabilizers[j]):
                anticommuting_pairs.append((i, j))
    
    if anticommuting_pairs:
        print(f"Found {len(anticommuting_pairs)} anticommuting pairs.")
        # Print first few
        for i, j in anticommuting_pairs[:5]:
            print(f"  {i}: {lines[i]}")
            print(f"  {j}: {lines[j]}")
            # print(f"  Anti-commutes at indices: {[k for k in range(85) if lines[i][k] != 'I' and lines[j][k] != 'I' and lines[i][k] != lines[j][k]]}")
    else:
        print("All stabilizers commute.")

    # Try to generate circuit
    print("Generating circuit...")
    try:
        # Check if tableau is consistent using Tableau.from_stabilizers
        # If allow_underconstrained=True, it will create a state that satisfies as many as possible
        # consistent with the others, or maybe just fill the rest with identities.
        # But if they are contradictory (anticommute), it might fail or drop some.
        # Let's see what happens.
        
        tableau = stim.Tableau.from_stabilizers(stabilizers, allow_underconstrained=True, allow_redundant=True)
        circuit = tableau.to_circuit("elimination")
        
        # Verify
        print("Verifying circuit...")
        sim = stim.TableauSimulator()
        sim.do_circuit(circuit)
        
        # Check if stabilizers are satisfied
        satisfied_count = 0
        for i, s in enumerate(stabilizers):
            # Measuring returns 0 for +1 eigenstate, 1 for -1 eigenstate (or random).
            # We want +1 eigenstate.
            # However, measuring collapses the state if not an eigenstate.
            # But here we are just checking if the generated circuit is correct.
            # So we can just measure them.
            # If the state is not an eigenstate, we will get random results and likely fail some checks.
            # If it is an eigenstate of -1, we get 1.
            
            # Use peek_observable_expectation if we don't want to collapse, but measure is fine for verification script.
            res = sim.measure_observable(s)
            if res == 0: # +1 eigenvalue
                satisfied_count += 1
            else:
                pass
                # print(f"Stabilizer {i} not satisfied (result {res})")

        print(f"Satisfied {satisfied_count}/{len(stabilizers)} stabilizers.")
        
        with open(r'C:\Users\anpaz\Repos\quantum-ai\rq1\circuit_85.stim', 'w') as f:
            f.write(str(circuit))
            
    except Exception as e:
        print(f"Error generating circuit: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    solve()
