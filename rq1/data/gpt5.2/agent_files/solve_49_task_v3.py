import stim
import sys

def solve():
    try:
        with open('stabilizers_49.txt', 'r') as f:
            lines = [line.strip() for line in f if line.strip()]

        print(f"Loaded {len(lines)} stabilizers")
        
        # Convert to stim.PauliString
        stabs = [stim.PauliString(line) for line in lines]
        
        # Check for anticommutativity
        print("Checking commutativity...")
        anticommuting_pairs = []
        for i in range(len(stabs)):
            for j in range(i + 1, len(stabs)):
                if not stabs[i].commutes(stabs[j]):
                    anticommuting_pairs.append((i, j))
        
        if anticommuting_pairs:
            print(f"Found {len(anticommuting_pairs)} anticommuting pairs!")
            # If there are anticommuting pairs, we can't satisfy all.
            # But the prompt says "generate a valid Stim circuit... that prepares the stabilizer state defined by these generators"
            # It usually implies a valid state exists. Maybe there are some redundant or conflicting ones?
            # Or maybe I copied them wrong? No, I copied from prompt.
            # If they anticommute, then there is NO common eigenstate.
            # Let's see if stim can handle it (maybe some are just errors in the problem statement, or I should drop some?)
            # Or maybe it's a code and I need to find a logical state?
            # The prompt says: "The final quantum state ... must be a +1 eigenstate of EVERY provided stabilizer generator."
            # This implies they MUST commute.
            # I will list them if any.
            for i, j in anticommuting_pairs[:5]:
                print(f"  {i} vs {j}")
        else:
            print("All stabilizers commute.")

        # Try to generate circuit using tableau method
        # allow_underconstrained=True is needed if < 49 independent stabilizers
        # allow_redundant=True is needed if > 49 or linear dependencies exist
        t = stim.Tableau.from_stabilizers(stabs, allow_underconstrained=True, allow_redundant=True)
        c = t.to_circuit("elimination")
        print("Circuit generated successfully")
        with open('circuit_49_generated_v3.stim', 'w') as f:
            f.write(str(c))
            
    except Exception as e:
        print(f"Failed to generate circuit: {e}")

if __name__ == "__main__":
    solve()
