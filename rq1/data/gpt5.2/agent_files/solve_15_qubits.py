import stim
import sys

def solve():
    stabilizers = [
        "XXXXXXXXIIIIIII",
        "IXXIXXIIXXIXXII",
        "IIXXIXXIIXXXIXI",
        "IIIIXXXXIIIXXXX",
        "ZZZZIIIIIIIIIII",
        "IZZIZZIIIIIIIII",
        "IIZZIZZIIIIIIII",
        "IIIIZZZZIIIIIII",
        "IZIIZIIIZIIIZII",
        "IIZIIZIIIZIZIII",
        "IIZZIIIIIZZIIII",
        "IIIIZZIIIIIZZII",
        "IIIIIZZIIIIZIZI",
        "IIIIIIZZIIIIIZZ"
    ]

    # Convert strings to PauliStrings
    pauli_stabilizers = [stim.PauliString(s) for s in stabilizers]

    # Create a Tableau from the stabilizers.
    # We use allow_underconstrained=True because 14 stabilizers on 15 qubits leaves 1 degree of freedom.
    # The tableau object will pick a valid state (e.g. by setting the logical qubit to |0> or |+> implicitly).
    # We just need to ensure the resulting state satisfies the given stabilizers.
    try:
        tableau = stim.Tableau.from_stabilizers(pauli_stabilizers, allow_underconstrained=True)
    except Exception as e:
        print(f"Error creating tableau: {e}")
        return

    # Generate a circuit that prepares this tableau from |0...0>
    circuit = tableau.to_circuit("elimination")

    # Verify the circuit
    sim = stim.TableauSimulator()
    sim.do(circuit)
    
    # Check if the state is a +1 eigenstate of all stabilizers
    all_good = True
    for s in pauli_stabilizers:
        # peek_observable_expectation returns +1, -1, or 0 (if random)
        expectation = sim.peek_observable_expectation(s)
        if expectation != 1:
            print(f"Stabilizer {s} not satisfied! Expectation: {expectation}")
            all_good = False
    
    if all_good:
        print("Circuit found and verified!")
        with open("circuit_15.stim", "w") as f:
            for instruction in circuit:
                if instruction.name == "CX":
                    targets = instruction.targets_copy()
                    # Split into pairs
                    for i in range(0, len(targets), 2):
                        f.write(f"CX {targets[i].value} {targets[i+1].value}\n")
                elif instruction.name == "H":
                    targets = instruction.targets_copy()
                    for t in targets:
                        f.write(f"H {t.value}\n")
                else:
                    f.write(str(instruction) + "\n")
        print("Circuit saved to circuit_15.stim (decomposed)")
    else:
        print("Circuit generated but failed verification.")

if __name__ == "__main__":
    solve()
