import stim
import numpy as np

# Read stabilizers from file
with open('data/gpt5.2/agent_files/stabs_196.txt', 'r') as f:
    stabs_str = [line.strip() for line in f if line.strip()]

print(f"Total stabilizers: {len(stabs_str)}")
n = len(stabs_str[0])
print(f"Number of qubits: {n}")

# Convert to stim PauliStrings
stabs = []
for s in stabs_str:
    ps = stim.PauliString(s)
    stabs.append(ps)

# Check commutativity and find anticommuting pairs
def commutes(ps1, ps2):
    """Check if two Pauli strings commute using stim's built-in."""
    return ps1.commutes(ps2)

# Find anticommuting pairs
anticomm_pairs = []
for i in range(len(stabs)):
    for j in range(i+1, len(stabs)):
        if not commutes(stabs[i], stabs[j]):
            anticomm_pairs.append((i, j))

print(f"Found {len(anticomm_pairs)} anticommuting pairs")
if anticomm_pairs:
    print(f"First few: {anticomm_pairs[:5]}")

# Try to find a maximal commuting subset using greedy approach
# Include stabilizers one by one if they commute with all already included
included = []
for i in range(len(stabs)):
    can_include = True
    for j in included:
        if not commutes(stabs[i], stabs[j]):
            can_include = False
            break
    if can_include:
        included.append(i)

print(f"Maximal commuting subset has {len(included)} stabilizers")

# Get the subset of stabilizers
subset_stabs = [stabs[i] for i in included]

# Try to create tableau from this subset
try:
    tableau = stim.Tableau.from_stabilizers(
        subset_stabs,
        allow_redundant=True,
        allow_underconstrained=True
    )
    circuit = tableau.to_circuit('elimination')
    print(f"Circuit generated with {len(circuit)} operations")
    
    # Save circuit - iterate through instructions to avoid line wrapping
    with open('data/gpt5.2/agent_files/circuit_196.stim', 'w') as f:
        for inst in circuit:
            f.write(str(inst) + '\n')
    print("Circuit saved to circuit_196.stim")
    
except Exception as e:
    print(f"Error: {e}")
