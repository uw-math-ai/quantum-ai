import stim
import sys

stabilizers = [
    stim.PauliString("IIXIXXX"),
    stim.PauliString("IXIXIXX"),
    stim.PauliString("XXXIIXI"),
    stim.PauliString("IIZIZZZ"),
    stim.PauliString("IZIZIZZ"),
    stim.PauliString("ZZZIIZI")
]

print("Checking commutativity...")
n = len(stabilizers)
all_commute = True
for i in range(n):
    for j in range(i + 1, n):
        if not stabilizers[i].commutes(stabilizers[j]):
            print(f"Stabilizers {i} and {j} anticommute!")
            all_commute = False

if all_commute:
    print("All stabilizers commute.")
else:
    print("Some stabilizers anticommute.")
    sys.exit(1)

try:
    tableau = stim.Tableau.from_stabilizers(stabilizers, allow_underconstrained=True)
    circuit = tableau.to_circuit("elimination")
    print("\nGenerated Circuit:")
    print(circuit)
    
    # Verify the circuit prepares the state
    sim = stim.TableauSimulator()
    sim.do(circuit)
    
    print("\nVerifying stabilizers:")
    for i, s in enumerate(stabilizers):
        expectation = sim.peek_observable_expectation(s)
        print(f"Stabilizer {i}: {expectation}")
        if expectation != 1:
            print(f"FAIL: Stabilizer {i} not satisfied")

    # Save to file
    with open("circuit_7_task.stim", "w") as f:
        f.write(str(circuit))
        
except Exception as e:
    print(f"Error: {e}")
