import stim
import sys

def solve():
    try:
        with open('stabilizers_135.txt', 'r') as f:
            stabs = [line.strip() for line in f if line.strip()]

        n_qubits = len(stabs[0])
        print(f"Number of stabilizers: {len(stabs)}")
        print(f"Qubits: {n_qubits}")
        
        # Verify all are same length
        for s in stabs:
            if len(s) != n_qubits:
                print(f"Error: Stabilizer {s} has length {len(s)}")
                return

        # Attempt to create a Tableau from stabilizers
        # If len(stabs) < n_qubits, we might need to pad.
        # But if it's == n_qubits, we can try to solve directly.
        
        if len(stabs) < n_qubits:
            print(f"Under-constrained: {len(stabs)} stabilizers for {n_qubits} qubits.")
            # If underconstrained, we can try to fill the rest with Zs on unused qubits, or just let Stim handle it if possible.
            # But Stim's Tableau.from_stabilizers doesn't invent stabilizers.
            # However, we can use the tableau algorithm to find a state.
            # Let's try to just run it and see if it fails.
            pass

        try:
            # allow_underconstrained=True is needed if fewer stabilizers than qubits
            tableau = stim.Tableau.from_stabilizers(stabs, allow_redundant=False, allow_underconstrained=True)
            circuit = tableau.to_circuit()
            with open('circuit_solution_135.stim', 'w') as f:
                f.write(str(circuit))
            print("Circuit generated successfully.")
        except Exception as e:
            print(f"Error generating tableau: {e}")
            
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    solve()
