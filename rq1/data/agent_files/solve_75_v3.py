import stim

def parse_stabilizers(filename):
    with open(filename, 'r') as f:
        lines = [line.strip() for line in f if line.strip()]
    return lines

stabilizers_str = parse_stabilizers('stabilizers_75.txt')
print(f"Loaded {len(stabilizers_str)} stabilizers.")

# Convert to stim.PauliString
stabilizers = [stim.PauliString(s) for s in stabilizers_str]

# Create tableau
# Using allow_underconstrained=True
# and allow_redundant=True just in case
try:
    t = stim.Tableau.from_stabilizers(stabilizers, allow_underconstrained=True, allow_redundant=True)
    print("Successfully created Tableau.")
    
    # Generate circuit
    # Use elimination method which is standard
    c = t.to_circuit(method="elimination")
    
    # Check circuit size
    print(f"Generated circuit with {len(c)} instructions.")
    
    # Add resets at the beginning
    full_circuit = stim.Circuit()
    full_circuit.append("R", range(75))
    full_circuit += c
    
    with open('circuit_75.stim', 'w') as f:
        f.write(str(full_circuit))
    print("Saved circuit to circuit_75.stim")
        
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
