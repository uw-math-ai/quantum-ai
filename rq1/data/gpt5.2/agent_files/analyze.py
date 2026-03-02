import stim

with open('data/gpt5.2/agent_files/stabs.txt', 'r') as f:
    stabilizers = [line.strip() for line in f if line.strip()]

print(f"Total stabilizers: {len(stabilizers)}")
print(f"Stabilizer length: {len(stabilizers[0])}")

# Analyze patterns
for i, s in enumerate(stabilizers[:5]):
    non_i = [(j, c) for j, c in enumerate(s) if c != 'I']
    print(f"s{i}: {non_i}")

print("...")

# Check for commutativity issues
def check_commute(s1, s2):
    count = 0
    for i in range(len(s1)):
        if s1[i] != 'I' and s2[i] != 'I' and s1[i] != s2[i]:
            count += 1
    return count % 2 == 0

anticomm_pairs = []
for i in range(len(stabilizers)):
    for j in range(i+1, len(stabilizers)):
        if not check_commute(stabilizers[i], stabilizers[j]):
            anticomm_pairs.append((i, j))

print(f"Anticommuting pairs: {len(anticomm_pairs)}")
if anticomm_pairs:
    print(f"First few: {anticomm_pairs[:5]}")

# Convert to stim PauliString format
stim_stabs = []
for s in stabilizers:
    stim_stabs.append(stim.PauliString('+' + s))

# Try to build circuit using stim
try:
    tab = stim.Tableau.from_stabilizers(stim_stabs, allow_underconstrained=True, allow_redundant=True)
    print(f"Tableau created successfully")
    circuit = tab.to_circuit(method='elimination')
    print(f"Circuit created: {len(circuit)} instructions")
    with open('data/gpt5.2/agent_files/circuit.stim', 'w') as f:
        f.write(str(circuit))
    print("Circuit saved to circuit.stim")
    print("Circuit preview:")
    print(str(circuit)[:1500])
except Exception as e:
    import traceback
    traceback.print_exc()
    print(f"Error: {e}")
