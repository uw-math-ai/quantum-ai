import stim
import sys

def solve():
    with open("stabilizers_56.txt", "r") as f:
        lines = [l.strip() for l in f if l.strip()]
    
    num_qubits = len(lines[0])
    print(f"Num qubits: {num_qubits}")
    print(f"Num stabilizers: {len(lines)}")

    stabilizers = [stim.PauliString(s) for s in lines]

    # Check commutation
    for i in range(len(stabilizers)):
        for j in range(i + 1, len(stabilizers)):
            if not stabilizers[i].commutes(stabilizers[j]):
                print(f"Stabilizers {i} and {j} do not commute!")
                return

    print("All stabilizers commute.")

    # Try to complete the stabilizers
    # We can use Tableau.from_stabilizers with allow_underconstrained=True
    # and then inspect the tableau to see what the other generators are.
    # Actually, from_stabilizers returns a Tableau that represents a specific state
    # consistent with the stabilizers. It fills in the gaps.
    
    try:
        tableau = stim.Tableau.from_stabilizers(stabilizers, allow_underconstrained=True)
        print("Successfully created tableau (possibly underconstrained).")
        
        # If we convert this tableau to a circuit, it will prepare the state corresponding
        # to the full set of stabilizers in the tableau (including the filled-in ones).
        # We just need to ensure that the filled-in ones don't contradict (they won't by definition)
        # and that the original ones are indeed stabilizers of the resulting state.
        
        # Let's verify the stabilizers on the tableau state.
        # The tableau represents a Clifford operation C such that the state is C|0>.
        # The stabilizers of C|0> are C Z_i C^dag.
        # stim's from_stabilizers constructs C such that the provided stabilizers are 
        # mapped from Z_i (or similar).
        
        # Actually, let's just generate the circuit and test it.
        circuit = tableau.to_circuit()
        print("Generated circuit length:", len(circuit))
        
        # Save circuit to file
        with open("circuit_candidate_56.stim", "w") as f:
            f.write(str(circuit))
            
    except Exception as e:
        print(f"Error creating tableau: {e}")

if __name__ == "__main__":
    solve()
