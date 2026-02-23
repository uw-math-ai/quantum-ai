import stim
import sys

def solve():
    with open('data/gemini-3-pro-preview/agent_files/stabilizers_135.txt', 'r') as f:
        stabs = [line.strip() for line in f if line.strip()]

    # Be careful with indices. Python list is 0-indexed.
    # Stab 119 is at index 119.
    
    # Check 44, 59, 119 again
    s44 = stabs[44]
    s59 = stabs[59]
    s119 = stabs[119]
    
    # Check anticommutativity
    p44 = stim.PauliString(s44)
    p59 = stim.PauliString(s59)
    p119 = stim.PauliString(s119)
    
    if not p44.commutes(p119):
        print(f"Confirmed: 44 and 119 anticommute")
    if not p59.commutes(p119):
        print(f"Confirmed: 59 and 119 anticommute")
        
    # Create new list without 119
    stabs_new = [s for i, s in enumerate(stabs) if i != 119]
    
    # Try generating circuit
    try:
        tableau = stim.Tableau.from_stabilizers(
            [stim.PauliString(s) for s in stabs_new],
            allow_underconstrained=True,
            allow_redundant=True
        )
    except Exception as e:
        print(f"Error creating tableau: {e}")
        return

    circuit = tableau.to_circuit("elimination")
    
    with open('data/gemini-3-pro-preview/agent_files/circuit_135_fixed.stim', 'w') as f:
        f.write(str(circuit))
    
    print("Circuit generated without stabilizer 119")

if __name__ == "__main__":
    solve()
