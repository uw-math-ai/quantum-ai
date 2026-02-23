import stim
import sys

def solve():
    try:
        with open(r"data\gemini-3-pro-preview\agent_files\stabilizers_136.txt", "r") as f:
            lines = [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        print("Error: File not found.")
        return

    stabilizers = []
    for line in lines:
        try:
            stabilizers.append(stim.PauliString(line))
        except ValueError as e:
            print(f"Error parsing line: {line}. {e}")
            return

    print(f"Loaded {len(stabilizers)} stabilizers.")
    if len(stabilizers) == 0:
        print("No stabilizers loaded.")
        return

    n = len(stabilizers[0])
    print(f"Qubits (from first stabilizer): {len(stabilizers[0])}")
    
    # Check if all same length
    for i, s in enumerate(stabilizers):
        if len(s) != n:
            print(f"Warning: Stabilizer {i} has length {len(s)}, expected {n}. Padding with I.")
            stabilizers[i] += stim.PauliString("I" * (n - len(s)))

    # Check commutativity
    print("Checking commutativity...")
    anticommuting_pairs = []
    for i in range(len(stabilizers)):
        s1 = stabilizers[i]
        for j in range(i + 1, len(stabilizers)):
            s2 = stabilizers[j]
            if not s1.commutes(s2):
                anticommuting_pairs.append((i, j))
    
    if anticommuting_pairs:
        print(f"Found {len(anticommuting_pairs)} anticommuting pairs.")
        for pair in anticommuting_pairs[:10]:
             print(f"  {pair} anticommute")
        if len(anticommuting_pairs) > 10:
            print("  ...")
    else:
        print("All stabilizers commute.")

    # Try to solve
    try:
        # stim.Tableau.from_stabilizers creates a tableau whose stabilizers include the given ones.
        # It requires the stabilizers to be independent and commuting.
        
        # If they anticommute, we can't use from_stabilizers directly.
        # But maybe we can drop anticommuting ones?
        # The task requires maximizing preserved stabilizers.
        # Let's try to find a maximal commuting set.
        
        if anticommuting_pairs:
             print("Anticommuting pairs found. Trying to find maximal commuting set...")
             # Greedy approach:
             # Keep a list of good stabilizers.
             # Add each stabilizer if it commutes with all existing good ones.
             
             good_stabilizers = []
             good_indices = []
             
             for i, s in enumerate(stabilizers):
                 commutes = True
                 for existing_s in good_stabilizers:
                     if not s.commutes(existing_s):
                         commutes = False
                         break
                 if commutes:
                     good_stabilizers.append(s)
                     good_indices.append(i)
             
             print(f"Found {len(good_stabilizers)} commuting stabilizers out of {len(stabilizers)}.")
             stabilizers = good_stabilizers

        tableau = stim.Tableau.from_stabilizers(stabilizers, allow_redundant=True, allow_underconstrained=True)
        circuit = tableau.to_circuit()
        print("Successfully generated circuit using stim.Tableau.from_stabilizers")
        
        # Verify the circuit
        print("Verifying circuit...")
        sim = stim.TableauSimulator()
        sim.do(circuit)
        
        # Check if the state satisfies the stabilizers
        satisfied = True
        for i, s in enumerate(stabilizers):
            if sim.peek_observable_expectation(s) != 1:
                print(f"Stabilizer {i} not satisfied.")
                satisfied = False
                break
        
        if satisfied:
            print("Circuit verified locally!")
            with open("circuit_136.stim", "w") as f:
                f.write(str(circuit))
        else:
            print("Circuit failed local verification.")

    except Exception as e:
        print(f"Failed to generate circuit: {e}")

if __name__ == "__main__":
    solve()
