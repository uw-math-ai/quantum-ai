import stim

# Parse stabilizers
stabilizers = [
    "XXXXIIIIIIIIIIIIIIIIIIIIIIII",
    "IIIIIIIXXXXIIIIIIIIIIIIIIIII",
    "IIIIIIIIIIIIIIXXXXIIIIIIIIII",
    "IIIIIIIIIIIIIIIIIIIIIXXXXIII",
    "XIXIXIXIIIIIIIIIIIIIIIIIIIII",
    "IIIIIIIXIXIXIXIIIIIIIIIIIIII",
    "IIIIIIIIIIIIIIXIXIXIXIIIIIII",
    "IIIIIIIIIIIIIIIIIIIIIXIXIXIX",
    "IIXXXXIIIIIIIIIIIIIIIIIIIIII",
    "IIIIIIIIIXXXXIIIIIIIIIIIIIII",
    "IIIIIIIIIIIIIIIIXXXXIIIIIIII",
    "IIIIIIIIIIIIIIIIIIIIIIIXXXXI",
    "ZZZZIIIIIIIIIIIIIIIIIIIIIIII",
    "IIIIIIIZZZZIIIIIIIIIIIIIIIII",
    "IIIIIIIIIIIIIIZZZZIIIIIIIIII",
    "IIIIIIIIIIIIIIIIIIIIIZZZZIII",
    "ZIZIZIZIIIIIIIIIIIIIIIIIIIII",
    "IIIIIIIZIZIZIZIIIIIIIIIIIIII",
    "IIIIIIIIIIIIIIZIZIZIZIIIIIII",
    "IIIIIIIIIIIIIIIIIIIIIZIZIZIZ",
    "IIZZZZIIIIIIIIIIIIIIIIIIIIII",
    "IIIIIIIIIZZZZIIIIIIIIIIIIIII",
    "IIIIIIIIIIIIIIIIZZZZIIIIIIII",
    "IIIIIIIIIIIIIIIIIIIIIIIZZZZI",
    "IXXIXIIIXXIXIIIXXIXIIIXXIXII",
    "IZZIZIIIZZIZIIIZZIZIIIZZIZII",
]

n_qubits = 28

def stab_to_stim(s):
    """Convert stabilizer string to stim format"""
    x_part = []
    z_part = []
    for i, c in enumerate(s):
        if c == 'X':
            x_part.append(i)
        elif c == 'Z':
            z_part.append(i)
        elif c == 'Y':
            x_part.append(i)
            z_part.append(i)
    return x_part, z_part

# Build stim stabilizers
stim_stabs = []
for s in stabilizers:
    x_part, z_part = stab_to_stim(s)
    stim_stab = stim.PauliString(n_qubits)
    for i in x_part:
        stim_stab[i] = 1  # X
    for i in z_part:
        if stim_stab[i] == 1:
            stim_stab[i] = 2  # Y
        else:
            stim_stab[i] = 3  # Z
    stim_stabs.append(stim_stab)

print(f"Parsed {len(stim_stabs)} stabilizers")

# Use Stim tableau to synthesize
try:
    tableau = stim.Tableau.from_stabilizers(stim_stabs, allow_redundant=True, allow_underconstrained=True)
    circuit = tableau.to_circuit(method='graph_state')
    
    # Replace RX with H (both create |+> from |0>)
    circuit_str = str(circuit)
    lines = circuit_str.strip().split('\n')
    new_lines = []
    for line in lines:
        if line.startswith('RX '):
            new_lines.append('H ' + line[3:])
        else:
            new_lines.append(line)
    circuit_str = '\n'.join(new_lines)
    
    print("Generated circuit (RX replaced with H):")
    print(circuit_str)
    
    # Save to file
    with open('data/gpt5.2/agent_files/candidate.stim', 'w') as f:
        f.write(circuit_str)
    print("\nSaved to candidate.stim")
    
except Exception as e:
    print(f"Error: {e}")