import stim
import numpy as np

def parse_stabilizers(filename):
    with open(filename, 'r') as f:
        lines = [line.strip() for line in f if line.strip()]
    # Remove line numbers if present (e.g. "1. XXX")
    cleaned_lines = []
    for line in lines:
        if '. ' in line[:5]:
            line = line.split('. ', 1)[1]
        cleaned_lines.append(line)
    return cleaned_lines

stabilizers = parse_stabilizers('stabilizers_161_fixed.txt')
print(f"Number of stabilizers: {len(stabilizers)}")
print(f"Length of first stabilizer: {len(stabilizers[0])}")

# Check commutativity
def check_commutativity(stabilizers):
    n = len(stabilizers)
    m = len(stabilizers[0])
    
    # Convert to symplectic form
    # X part: 1 if X or Y
    # Z part: 1 if Z or Y
    xs = np.zeros((n, m), dtype=bool)
    zs = np.zeros((n, m), dtype=bool)
    
    for i, s in enumerate(stabilizers):
        for j, char in enumerate(s):
            if char in 'XZY':
                if char in 'XY':
                    xs[i, j] = True
                if char in 'ZY':
                    zs[i, j] = True
                    
    comm_matrix = (xs @ zs.T) ^ (zs @ xs.T)
    return comm_matrix

comm_matrix = check_commutativity(stabilizers)
anticommuting_pairs = np.argwhere(comm_matrix)
print(f"Number of anticommuting pairs: {len(anticommuting_pairs) // 2}")

if len(anticommuting_pairs) > 0:
    print("Anticommuting pairs (indices):")
    for i, j in anticommuting_pairs:
        if i < j:
            print(f"{i} vs {j}")
else:
    print("All stabilizers commute.")

# Try to solve using stim
try:
    tableau = stim.Tableau.from_stabilizers([stim.PauliString(s) for s in stabilizers], allow_underconstrained=True)
    print("Successfully created tableau from stabilizers.")
    circuit = tableau.to_circuit()
    print("Circuit generated.")
    with open('circuit_161_generated.stim', 'w') as f:
        f.write(str(circuit))
except Exception as e:
    print(f"Failed to create tableau: {e}")
