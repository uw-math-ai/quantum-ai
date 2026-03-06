import stim
import sys

def load_stabilizers(filename):
    with open(filename, 'r') as f:
        lines = [line.strip() for line in f if line.strip()]
    return lines

def solve():
    stabilizers = load_stabilizers(r"C:\Users\anpaz\Repos\quantum-ai\rq1\data\gemini-3-pro-preview\agent_files\stabs_161.txt")
    print(f"Loaded {len(stabilizers)} stabilizers.")
    
    # Create tableau allowing underconstrained
    try:
        t = stim.Tableau.from_stabilizers([stim.PauliString(s) for s in stabilizers], allow_underconstrained=True)
        print("Tableau created.")
    except Exception as e:
        print(f"Error creating tableau: {e}")
        return

    # Stim's to_circuit() on a Tableau produces the operations to implement the Clifford map.
    # If the tableau represents a state (stabilizers mapped from Z bases), then applying this circuit to |0> state should prepare it?
    # No, from_stabilizers returns a Tableau T such that T(Z_k) = S_k (roughly).
    # If we start with |0> state (stabilized by Z_0, Z_1, ...), and apply T,
    # the new state is stabilized by T(Z_k) T^\dagger.
    # Wait, let's verify what from_stabilizers does.
    # It finds a Tableau T such that for the first N stabilizers S_k, T(Z_k) = S_k.
    # So if we apply T to the state |0...0> (which is stabilized by Z_0, ..., Z_{n-1}),
    # the resulting state will be stabilized by S_0, ..., S_{n-1}.
    
    # However, since we have 160 stabilizers and 161 qubits, T will map Z_0...Z_{159} to the stabilizers.
    # The last qubit 160 is unconstrained.
    
    circuit = t.to_circuit()
    
    # We need to print the circuit to a file or stdout
    print("Generated circuit.")
    with open(r"C:\Users\anpaz\Repos\quantum-ai\rq1\data\gemini-3-pro-preview\agent_files\circuit_161.stim", "w") as f:
        f.write(str(circuit))

if __name__ == "__main__":
    solve()
