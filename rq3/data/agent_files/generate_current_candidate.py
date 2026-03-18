import stim

# Load stabilizers
with open(r'C:\Users\anpaz\Repos\quantum-ai\rq3\current_target_stabilizers.txt', 'r') as f:
    lines = [l.strip() for l in f.readlines() if l.strip()]

stabilizers = lines
num_stabilizers = len(stabilizers)
print(f"Loaded {num_stabilizers} stabilizers.")
if num_stabilizers > 0:
    print(f"First stabilizer length: {len(stabilizers[0])}")

# Load baseline to check qubit count
with open(r'C:\Users\anpaz\Repos\quantum-ai\rq3\current_baseline.stim', 'r') as f:
    circuit_text = f.read()

circuit = stim.Circuit(circuit_text)
num_qubits = circuit.num_qubits
print(f"Baseline circuit num_qubits: {num_qubits}")

# Check consistency
if len(stabilizers[0]) != num_qubits:
    print(f"Warning: Stabilizer length {len(stabilizers[0])} != Circuit num_qubits {num_qubits}")
    # Force use of stabilizer length
    num_qubits = len(stabilizers[0])
else:
    print("Stabilizer length matches Circuit num_qubits.")

# Attempt synthesis
try:
    print("Attempting synthesis with method='graph_state'...")
    # stim.Tableau.from_stabilizers expects a list of Pauli strings
    tableau = stim.Tableau.from_stabilizers(stabilizers, allow_redundant=True, allow_underconstrained=True)
    
    # Generate circuit
    new_circuit = tableau.to_circuit(method='graph_state')
    
    # Output metrics
    cx_count = new_circuit.num_gates("CX")
    cz_count = new_circuit.num_gates("CZ")
    print(f"Synthesized circuit stats: CX={cx_count}, CZ={cz_count}")
    
    with open(r'C:\Users\anpaz\Repos\quantum-ai\rq3\candidate_graph.stim', 'w') as f:
        f.write(str(new_circuit))
    print("Saved to candidate_graph.stim")
    
except Exception as e:
    print(f"Synthesis failed: {e}")
