import stim

with open('baseline.stim', 'r') as f:
    circuit = stim.Circuit(f.read())

cx_count = circuit.num_gates('CX') + circuit.num_gates('CNOT')
volume = sum(1 for op in circuit if op.name in ['CX', 'CNOT', 'CZ', 'H', 'S', 'SQRT_X', 'X', 'Y', 'Z'])
# Note: Volume usually counts all 1 and 2 qubit gates. Stim has many gates.
# The evaluate_optimization tool uses a specific metric.
# It's better to rely on evaluate_optimization output for comparison.
# But for now, let's just print basic info.

print(f"Baseline CX count: {cx_count}")
print(f"Baseline ops: {len(circuit)}")
