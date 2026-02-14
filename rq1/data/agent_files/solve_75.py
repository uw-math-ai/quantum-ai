import stim
import sys

def parse_stabilizers(filename):
    with open(filename, 'r') as f:
        lines = [line.strip() for line in f if line.strip()]
    return lines

stabilizers = parse_stabilizers('stabilizers_75.txt')
print(f"Loaded {len(stabilizers)} stabilizers.")

# Check length
num_qubits = len(stabilizers[0])
print(f"Number of qubits: {num_qubits}")

# Create a tableau from stabilizers
# efficient method:
# 1. Create a Tableau.
# 2. But wait, from_stabilizers requires a full set of n stabilizers (Z stabilizers) and n destabilizers (X stabilizers) usually, 
#    or at least n stabilizers to define a state.
#    Here we have some number of stabilizers. Let's count them.

print(f"Number of stabilizers: {len(stabilizers)}")

if len(stabilizers) == num_qubits:
    print("Full set of stabilizers provided.")
    try:
        t = stim.Tableau.from_stabilizers(stabilizers)
        print("Successfully created Tableau from stabilizers.")
        c = t.to_circuit()
        print("Circuit generated.")
        with open('circuit_75.stim', 'w') as f:
            f.write(str(c))
    except Exception as e:
        print(f"Error creating tableau: {e}")
else:
    print("Not a full set of stabilizers.")
