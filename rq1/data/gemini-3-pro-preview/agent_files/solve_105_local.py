import stim
import sys

def solve():
    # Read stabilizers
    with open(r'C:\Users\anpaz\Repos\quantum-ai\rq1\data\gemini-3-pro-preview\agent_files\current_stabilizers.txt', 'r') as f:
        lines = [l.strip() for l in f if l.strip()]

    print(f"Read {len(lines)} stabilizers.")
    
    # Create Stim PauliStrings
    try:
        stabilizers = [stim.PauliString(s) for s in lines]
    except Exception as e:
        print(f"Error parsing stabilizers: {e}")
        return

    # Check for consistency
    print("Checking commutativity...")
    anticommuting_pairs = []
    for i in range(len(stabilizers)):
        for j in range(i + 1, len(stabilizers)):
            if not stabilizers[i].commutes(stabilizers[j]):
                anticommuting_pairs.append((i, j))
    
    if anticommuting_pairs:
        print(f"Found {len(anticommuting_pairs)} anticommuting pairs.")
        # If there are only a few, we might list them.
        for i, j in anticommuting_pairs[:10]:
             print(f"  {i} vs {j}: {lines[i]} vs {lines[j]}")
        # If inconsistent, we can't create a state that satisfies ALL.
        # But we can try to satisfy the maximum number. 
        # For now, let's see if we can satisfy the commuting ones.
    else:
        print("All stabilizers commute.")

    # Try to generate circuit
    try:
        # allow_underconstrained=True because we might have fewer than N stabilizers
        tableau = stim.Tableau.from_stabilizers(stabilizers, allow_underconstrained=True, allow_redundant=True)
        circuit = tableau.to_circuit("elimination")
        print("Successfully generated circuit.")
        
        # Verify locally
        print("Verifying locally...")
        sim = stim.TableauSimulator()
        sim.do_circuit(circuit)
        
        failures = 0
        for i, s in enumerate(stabilizers):
            res = sim.measure_observable(s)
            if res != 0: # 0 means +1 eigenvalue, 1 means -1 eigenvalue
                # It might be -1, but we want +1. 
                # If we get -1, it means we prepared the -1 eigenstate. 
                # However, from_stabilizers should prepare +1 if possible.
                # If it's -1, it might be due to sign in PauliString? 
                # The input strings are just Paulis, implying +1 phase.
                # Let's check if the measurement is deterministic.
                failures += 1
                
        print(f"Local verification: {len(stabilizers) - failures}/{len(stabilizers)} satisfied.")
        
        with open(r'C:\Users\anpaz\Repos\quantum-ai\rq1\data\gemini-3-pro-preview\agent_files\circuit.stim', 'w') as f:
            f.write(str(circuit))
            
    except Exception as e:
        print(f"Error generating circuit: {e}")

if __name__ == "__main__":
    solve()
