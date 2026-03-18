import stim
import sys

# Load files
with open("current_target_stabilizers.txt", "r") as f:
    stabilizers_str = [line.strip() for line in f if line.strip()]

stabilizers = [stim.PauliString(s) for s in stabilizers_str]

with open("current_baseline.stim", "r") as f:
    baseline_str = f.read()

baseline = stim.Circuit(baseline_str)
num_qubits = baseline.num_qubits
print(f"Num qubits: {num_qubits}")

# Verify baseline metrics
cx_count = 0
for instruction in baseline:
    if instruction.name == "CX" or instruction.name == "CNOT":
        cx_count += len(instruction.targets_copy()) // 2

print(f"Baseline CX count (approx): {cx_count}")

# Strategy 1: Graph State Synthesis
try:
    tableau = stim.Tableau.from_stabilizers(stabilizers, allow_underconstrained=True)
    
    # Synthesize using graph_state method
    circuit_graph = tableau.to_circuit(method="graph_state")
    
    with open("candidate_graph.stim", "w") as f:
        f.write(str(circuit_graph))
    print("Graph state synthesis successful")
        
except Exception as e:
    print(f"Graph state synthesis failed: {e}")

# Strategy 2: Elimination Synthesis
try:
    if 'tableau' in locals():
        circuit_elim = tableau.to_circuit(method="elimination")
        with open("candidate_elim.stim", "w") as f:
            f.write(str(circuit_elim))
        print("Elimination synthesis successful")
except Exception as e:
    print(f"Elimination synthesis failed: {e}")

