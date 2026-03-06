import stim
import os

def solve():
    stabilizers_path = r"C:\Users\anpaz\Repos\quantum-ai\rq1\stabilizers_161_current.txt"
    with open(stabilizers_path, "r") as f:
        stabilizers = [line.strip() for line in f if line.strip()]

    print(f"Read {len(stabilizers)} stabilizers.")
    
    # Fix stabilizer 28
    # Original: XXXXIIXIIXXIIIIIIXIIII...
    # Expected: XXXXIIIXIIXXIIIIIIXII... (based on pattern)
    # The original is: XXXX II XII XX IIIIII X IIII...
    # The pattern is:  XXXX III XII XX IIIIII X IIII...
    # So I need to insert an I after the first 4 Xs.
    
    s28 = stabilizers[28]
    # Check if it matches the 'bad' pattern
    if s28.startswith("XXXXIIXIIXX"):
        print("Stabilizer 28 matches the suspicious pattern.")
        # Try to fix it
        # Insert I at index 4 (0-based) to make it length 161
        s28_fixed = s28[:4] + "I" + s28[4:]
        print(f"Original length: {len(s28)}")
        print(f"Fixed length:    {len(s28_fixed)}")
        
        stabilizers[28] = s28_fixed
    else:
        print("Stabilizer 28 does not match the expected bad pattern.")

    # Convert to Stim PauliStrings
    try:
        pauli_strings = [stim.PauliString(s) for s in stabilizers]
    except Exception as e:
        print(f"Error parsing stabilizers: {e}")
        return

    # Check for commutativity
    print("Checking commutativity...")
    anticommuting_pairs = []
    for i in range(len(pauli_strings)):
        for j in range(i + 1, len(pauli_strings)):
            if not pauli_strings[i].commutes(pauli_strings[j]):
                anticommuting_pairs.append((i, j))
    
    if anticommuting_pairs:
        print(f"Found {len(anticommuting_pairs)} anticommuting pairs.")
        for i, j in anticommuting_pairs:
            print(f"  {i} vs {j}")
    else:
        print("All stabilizers commute with the fix!")
        
        # Try to generate circuit
        try:
            tableau = stim.Tableau.from_stabilizers(pauli_strings, allow_underconstrained=True, allow_redundant=True)
            circuit = tableau.to_circuit("elimination")
            print("Circuit generated successfully.")
            
            output_path = r"C:\Users\anpaz\Repos\quantum-ai\rq1\circuit_161_fixed.stim"
            with open(output_path, "w") as f:
                f.write(str(circuit))
            print(f"Circuit written to {output_path}")
        except Exception as e:
            print(f"Error generating circuit: {e}")

if __name__ == "__main__":
    solve()
