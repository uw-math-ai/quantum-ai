
import stim

# The raw string from the prompt
raw_stabs = """
IIXIIXIIIIIIIIIIIIIIIIIIIXIIXII, IIIIIIIIIIXIIXIIIIIIIXIIIIIXIII, IIIIIIIIIIIIXIIXIIIIIIIXIIIIIIX, IXIIXIIIIIIIIIIIIIIIIIIIXIXIIII, IIIIIIXXIIIIIIXIXIIIIIIIIIIIIII, IIIIIIIIXXIIIIIIIIXIXIIIIIIIIII, IIIIIIIIIIIIIIIIIIIXIIXIIXIIXII, IIIXIIIIIIXXIXIIIIIIIIIIIIIIIII, IIIIXIIIIIIIIIIIIIIIIXIIIIXXIII, IIIIIXXIIIIIXIIXXIIIIIXIIIIIXXI, IIIIIIIIXIIIIIIIIIXIIIIXIIIIIIX, XIIXIIIXIIXIIIXIIIIIIXIIXIXIIII, XIIIIIXXIIIIIIIIIIIIIIIIIIIIIXI, IXIIIIIIXXIIIIXXXIIIIIIIXIIIIIX, IIXIIIIIIIIIIIIIIXIXIIIIIXIIIII, IIZIIZIIIIIIIIIIIIIIIIIIIZIIZII, IIIIIIIIIIZIIZIIIIIIIZIIIIIZIII, IIIIIIIIIIIIZIIZIIIIIIIZIIIIIIZ, IZIIZIIIIIIIIIIIIIIIIIIIZIZIIII, IIIIIIZZIIIIIIZIZIIIIIIIIIIIIII, IIIIIIIIZZIIIIIIIIZIZIIIIIIIIII, IIIIIIIIIIIIIIIIIIIZIIZIIZIIZII, IIIZIIIIIIZZIZIIIIIIIIIIIIIIIII, IIIIZIIIIIIIIIIIIIIIIZIIIIZZIII, IIIIIZZIIIIIZIIZZIIIIIZIIIIIZZI, IIIIIIIIZIIIIIIIIIZIIIIZIIIIIIZ, ZIIZIIIZIIZIIIZIIIIIIZIIZIZIIII, ZIIIIIZZIIIIIIIIIIIIIIIIIIIIIZI, IZIIIIIIZZIIIIZZZIIIIIIIZIIIIIZ, IIZIIIIIIIIIIIIIIZIZIIIIIZIIIII
"""

# Parse
stabs = [s.strip() for s in raw_stabs.replace('\n', '').split(',') if s.strip()]

print(f"Found {len(stabs)} stabilizers.")
print(f"Length of first: {len(stabs[0])}")

# Check all lengths
for i, s in enumerate(stabs):
    if len(s) != 31:
        print(f"Error: Stabilizer {i} has length {len(s)}")

# Convert to Stim objects
stim_stabs = [stim.PauliString(s) for s in stabs]

# Check commutativity
commutes = True
for i in range(len(stim_stabs)):
    for j in range(i+1, len(stim_stabs)):
        if not stim_stabs[i].commutes(stim_stabs[j]):
            print(f"Anti-commutes: {i} and {j}")
            commutes = False

if not commutes:
    print("Stabilizers do not commute!")
else:
    print("All stabilizers commute.")

# Try to solve
try:
    tableau = stim.Tableau.from_stabilizers(stim_stabs, allow_underconstrained=True)
    circuit = tableau.to_circuit("elimination")
    
    print("Circuit generated successfully.")
    print(f"Circuit operations: {len(circuit)}")
    
    with open("circuit_solution.stim", "w") as f:
        f.write(str(circuit))
        
except Exception as e:
    print(f"Error generating circuit: {e}")
