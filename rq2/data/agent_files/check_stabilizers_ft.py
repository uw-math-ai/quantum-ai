import stim

# 1. Load circuit
with open("input_circuit_ft.stim", "r") as f:
    circuit = stim.Circuit(f.read())

sim = stim.TableauSimulator()
sim.do(circuit)

# 2. Define the Pauli string from the error report
# Error from report:
# loc: 6, gate: H, fault_qubit: 36, fault_pauli: Y
# Final Paulis:
# 0: X, 1: X, 2: X, 7: X, 8: X, 9: X, 14: X, 15: X, 16: X, 
# 21: X, 22: X, 23: X, 28: X, 29: Y, 30: X, 31: Z, 33: Z, 
# 35: X, 36: X, 37: X
# Note: 29: Y, 31: Z, 33: Z. Others X.

pauli_map = {
    0: 'X', 1: 'X', 2: 'X', 7: 'X', 8: 'X', 9: 'X', 14: 'X', 15: 'X', 16: 'X',
    21: 'X', 22: 'X', 23: 'X', 28: 'X', 29: 'Y', 30: 'X', 31: 'Z', 33: 'Z',
    35: 'X', 36: 'X', 37: 'X'
}

# Construct full Pauli string
# Max qubit index is 41
num_qubits = 42
pauli_str = ['I'] * num_qubits
for q, p in pauli_map.items():
    if q < num_qubits:
        pauli_str[q] = p
    
pauli_string = stim.PauliString("".join(pauli_str))

print(f"Checking Pauli: {pauli_string}")

# 3. Check expectation
expectation = sim.peek_observable_expectation(pauli_string)
print(f"Expectation: {expectation}")

if expectation == 1:
    print("RESULT: STABILIZER")
elif expectation == -1:
    print("RESULT: -STABILIZER")
elif expectation == 0:
    print("RESULT: NOT A STABILIZER (LOGICAL or ERROR)")
else:
    print(f"RESULT: {expectation}")
