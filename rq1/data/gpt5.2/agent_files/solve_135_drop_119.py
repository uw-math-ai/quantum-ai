import stim
from analyze_stabilizers_135 import stabilizers

padded_stabilizers = [s.strip().ljust(135, 'I') for s in stabilizers]

# Drop stabilizer 119
dropped_stabilizers = [s for i, s in enumerate(padded_stabilizers) if i != 119]

print(f"Total stabilizers after dropping 119: {len(dropped_stabilizers)}")

# Check for consistency
paulis = [stim.PauliString(s) for s in dropped_stabilizers]
anticommuting = False
for i in range(len(paulis)):
    for j in range(i + 1, len(paulis)):
        if not paulis[i].commutes(paulis[j]):
            print(f"Anticommute: {i} and {j}")
            anticommuting = True

if not anticommuting:
    print("All remaining stabilizers commute.")
    # Generate circuit
    try:
        tableau = stim.Tableau.from_stabilizers(
            paulis,
            allow_redundant=True,
            allow_underconstrained=True
        )
        circuit = tableau.to_circuit(method="elimination")
        print("Circuit generated.")
        
        # Save to file
        with open("circuit_135_drop_119.stim", "w") as f:
            f.write(str(circuit))
            
    except Exception as e:
        print(f"Error generating circuit: {e}")
else:
    print("Stabilizers still anticommute.")
