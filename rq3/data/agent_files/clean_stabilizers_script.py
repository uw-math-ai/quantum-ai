import stim
import sys
import os

# Read raw stabilizers
input_path = r'C:\Users\anpaz\Repos\quantum-ai\rq3\target_stabilizers_raw.txt'
output_path = r'C:\Users\anpaz\Repos\quantum-ai\rq3\target_stabilizers_clean.txt'

with open(input_path, 'r') as f:
    content = f.read().strip()

# Handle potential comma separation or newlines
if ',' in content:
    stabilizers = [s.strip() for s in content.split(',') if s.strip()]
else:
    stabilizers = [s.strip() for s in content.split('\n') if s.strip()]

# Remove any empty strings
stabilizers = [s for s in stabilizers if len(s) > 0]

print(f"Found {len(stabilizers)} stabilizers.")

# Check length consistency
lengths = [len(s) for s in stabilizers]
if not lengths:
    print("No stabilizers found.")
    sys.exit(1)

print(f"Lengths: min={min(lengths)}, max={max(lengths)}")

if min(lengths) != max(lengths):
    print("WARNING: Stabilizer lengths are inconsistent!")
    # count distribution
    from collections import Counter
    print(Counter(lengths))
else:
    print(f"All stabilizers have length {lengths[0]}")

# Write to clean file
with open(output_path, 'w') as f:
    for s in stabilizers:
        f.write(s + '\n')

# Also try to parse with stim to verify
try:
    tableau = stim.Tableau.from_stabilizers(stabilizers)
    print("Successfully parsed stabilizers into a tableau.")
    print(f"Tableau shape: {len(tableau)} qubits")
    # Verify the stabilizers are independent and N stabilizers for N qubits
    # If tableau length is equal to stabilizer count and qubit count, it is a stabilizer state
    # But usually Tableau.from_stabilizers creates a tableau of size N
    # where N is the length of the string.
    # The tableau might have internal size N.
except Exception as e:
    print(f"Error parsing stabilizers: {e}")
