import stim
import os

script_dir = os.path.dirname(os.path.abspath(__file__))
stabilizers_path = os.path.join(script_dir, 'stabilizers_119.txt')

print(f"Reading from {stabilizers_path}")
with open(stabilizers_path, 'r') as f:
    lines = [line.strip().replace(',', '') for line in f if line.strip()]

stabilizers = []
for line in lines:
    if not line:
        continue
    try:
        stabilizers.append(stim.PauliString(line))
    except:
        pass

print(f"Number of stabilizers: {len(stabilizers)}")
if stabilizers:
    print(f"Number of qubits: {len(stabilizers[0])}")

try:
    stim.Tableau.from_stabilizers(stabilizers, allow_underconstrained=True, allow_redundant=False)
    print("Stabilizers are independent.")
except Exception as e:
    print(f"Stabilizers are NOT independent: {e}")
