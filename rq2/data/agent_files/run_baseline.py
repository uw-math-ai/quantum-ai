
import sys
import stim

# Read input circuit
with open(r'C:\Users\anpaz\Repos\quantum-ai\rq2\input.stim', 'r') as f:
    circuit_str = f.read()

# Read stabilizers
with open(r'C:\Users\anpaz\Repos\quantum-ai\rq2\stabilizers.txt', 'r') as f:
    stabs_str = f.read()

stabilizers = [s.strip() for s in stabs_str.split(',') if s.strip()]

data_qubits = list(range(84))
flag_qubits = []

print(f"CIRCUIT_START")
print(circuit_str)
print(f"CIRCUIT_END")
print(f"STABILIZERS_START")
print(str(stabilizers))
print(f"STABILIZERS_END")
print(f"DATA_QUBITS_START")
print(str(data_qubits))
print(f"DATA_QUBITS_END")
print(f"FLAG_QUBITS_START")
print(str(flag_qubits))
print(f"FLAG_QUBITS_END")
