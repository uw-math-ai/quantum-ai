import stim

# Load circuit
with open("circuit_54_v2.stim", "r") as f:
    circuit_text = f.read()

circuit = stim.Circuit(circuit_text)

# The failing stabilizer
fail_stab = "IIIIIIIIIIIIIIIIIIIIIIIIIIIIIXIIXIIIIIIIIIIIIIIIIIIIII"

sim = stim.TableauSimulator()
sim.do_circuit(circuit)

val = sim.peek_observable_expectation(stim.PauliString(fail_stab))
print(f"Expectation: {val}")

# Also check if the circuit acts on correct qubits
print(f"Num qubits in circuit: {circuit.num_qubits}")
