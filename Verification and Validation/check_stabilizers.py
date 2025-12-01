import stim

# Example: Check if a circuit prepares the |0000⟩ + |1111⟩ state (4-qubit GHZ)
# This state is stabilized by: XXXX, ZIZI, IZZI, IIZZ

# Circuit that should prepare this state
circuit = stim.Circuit("""
    H 0
    CX 0 1
    CX 1 2
    CX 2 3
""")

# Define your target stabilizers
target_stabilizers = [
    stim.PauliString("XXXX"),
    stim.PauliString("ZIZI"),
    stim.PauliString("IZZI"),
    stim.PauliString("IIZZ"),
]

# Method 3: Use stim's stabilizer flow checker
print("=" * 60)
print("Method 3: Check specific Pauli expectations")
print("=" * 60)

# Simulate the circuit
sim = stim.TableauSimulator()
sim.do(circuit)

print("Checking if state is +1 eigenstate of target operators:")
for i, pauli in enumerate(target_stabilizers):
    expectation = sim.peek_observable_expectation(pauli)
    eigenvalue = "+1" if expectation > 0 else "-1"
    status = "✓" if expectation > 0 else "✗"
    print(f"  {pauli}: eigenvalue = {eigenvalue} {status}")