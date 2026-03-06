import stim
import sys

def solve():
    # Read stabilizers
    filename = r"C:\Users\anpaz\Repos\quantum-ai\rq1\data\gemini-3-pro-preview\agent_files\stabilizers_150_v2.txt"
    try:
        with open(filename, "r") as f:
            stabilizers = [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        print(f"Error: {filename} not found.")
        return

    print(f"Loaded {len(stabilizers)} stabilizers.")
    
    # Try to solve using stim
    try:
        # Convert strings to stim.PauliString
        pauli_stabilizers = [stim.PauliString(s) for s in stabilizers]
        
        # Check dimensions
        n_qubits = len(stabilizers[0])
        print(f"Stabilizer length: {n_qubits}")
        print(f"Number of stabilizers: {len(stabilizers)}")
        
        if len(stabilizers) < n_qubits:
            print("Warning: Fewer stabilizers than qubits. This defines a subspace, not a unique state.")
            # We can still find a state in this subspace.
            # But stim.Tableau.from_stabilizers expects a full set of n stabilizers for n qubits?
            # Documentation says: "Returns a Tableau capable of preparing a state stabilized by the given stabilizers."
            # If fewer, it might pick arbitrary stabilizers to complete the set?
            # Or it might fail if they are not independent.
            # Let's see what happens.
            # Actually, check_stabilizers_tool likely expects a full state preparation?
            # The prompt says "The final quantum state on the data qubits must be a +1 eigenstate of every provided stabilizer generator."
            # It doesn't say it must be a UNIQUE state. So any state in the subspace is fine.
            # However, from_stabilizers requires n stabilizers.
            # We can fill the rest with dummy stabilizers (e.g. Z on the remaining degrees of freedom) if needed,
            # provided they commute with the given ones.
            # But first let's see if it works as is.
            pass

        tableau = stim.Tableau.from_stabilizers(pauli_stabilizers, allow_underconstrained=True, allow_redundant=True)
        circuit = tableau.to_circuit()
        
        output_filename = r"C:\Users\anpaz\Repos\quantum-ai\rq1\data\gemini-3-pro-preview\agent_files\circuit_150_v2.stim"
        with open(output_filename, "w") as f:
            f.write(str(circuit))
        print("Circuit generated successfully.")
        print(f"Output saved to {output_filename}")
        
    except Exception as e:
        print(f"Error generating circuit: {e}")

if __name__ == "__main__":
    solve()
