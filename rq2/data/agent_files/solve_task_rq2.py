import stim
import sys
import re

# Read data
with open("stabilizers_rq2.txt") as f:
    stabilizers = f.read().splitlines()
with open("circuit_rq2.stim") as f:
    circuit_str = f.read()

# Determine data qubits: 0 to 53 (from circuit and stabilizers)
# Stabilizers len is 54. So qubits are 0..53.
data_qubits = list(range(54))

# We will define a function to call the validate_circuit tool.
# Since we are running in python, we can't call the tool directly.
# BUT, the AI (me) calls the tool.
# This script is just to help me parse things if needed.

# But I can't call the tool from this script.
# So I will just use this script to identify if I need to do any preprocessing.

# Check length
print(f"Len of first stabilizer: {len(stabilizers[0])}")
print(f"Len of last stabilizer: {len(stabilizers[-1])}")


# Check for Z stabilizers on qubit 48
print("\nChecking Z stabilizers on qubit 48:")
z_stabs_on_48 = []
for idx, s in enumerate(stabilizers):
    # s is string of length 54
    if len(s) > 48 and s[48] == 'Z':
        z_stabs_on_48.append(idx)
        print(f"Stabilizer {idx} has Z on 48: {s}")

if not z_stabs_on_48:
    print("No Z stabilizer on qubit 48 found.")

