import stim
import os

stabilizer_file = r"C:\Users\anpaz\Repos\quantum-ai\rq1\stabilizers_90.txt"
with open(stabilizer_file, "r") as f:
    stabilizers = [line.strip() for line in f if line.strip()]

num_qubits = 90
# Try to construct a Tableau from these stabilizers
try:
    # We want a tableau that outputs these stabilizers for Z inputs.
    # However, Stim's Tableau.from_stabilizers creates a tableau where the Z outputs are the stabilizers.
    # This means the tableau T maps Z_i -> S_i.
    # So if we apply T to |0> (which is stabilized by Z_i), we get a state stabilized by S_i.
    # So T is exactly the unitary we want.
    t = stim.Tableau.from_stabilizers([stim.PauliString(s) for s in stabilizers], allow_underconstrained=True)
    
    # Generate the circuit
    circuit = t.to_circuit("elimination")
    
    # Save the circuit
    with open(r"C:\Users\anpaz\Repos\quantum-ai\rq1\solve_90_circuit.stim", "w") as f:
        f.write(str(circuit))
        
    print(f"Generated circuit with {len(circuit)} instructions.")

except Exception as e:
    print(f"Error: {e}")
