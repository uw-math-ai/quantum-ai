import stim

# Reconstruct the first 72 stabilizers based on the pattern
# Qubits: 84
# Pattern: shift 7 * k for k in 0..11
# Blocks: XXXX, XIXIXIX, IIXXXX, ZZZZ, ZIZIZIZ, IIZZZZ

stabs = []

# Block 0: XXXX
base = "XXXX" + "I" * 80
for k in range(12):
    s = "I" * (7 * k) + base[:84 - 7 * k]
    stabs.append(s)

# Block 1: XIXIXIX
base = "XIXIXIX" + "I" * 77
for k in range(12):
    s = "I" * (7 * k) + base[:84 - 7 * k]
    stabs.append(s)

# Block 2: IIXXXX (Shifted by 2)
base = "IIXXXX" + "I" * 78
for k in range(12):
    s = "I" * (7 * k) + base[:84 - 7 * k]
    stabs.append(s)

# Block 3: ZZZZ
base = "ZZZZ" + "I" * 80
for k in range(12):
    s = "I" * (7 * k) + base[:84 - 7 * k]
    stabs.append(s)

# Block 4: ZIZIZIZ
base = "ZIZIZIZ" + "I" * 77
for k in range(12):
    s = "I" * (7 * k) + base[:84 - 7 * k]
    stabs.append(s)

# Block 5: IIZZZZ (Shifted by 2)
base = "IIZZZZ" + "I" * 78
for k in range(12):
    s = "I" * (7 * k) + base[:84 - 7 * k]
    stabs.append(s)

# Last 10 from prompt (verified length 84)
last_10 = [
    "IXXIXIIIXXIXIIIXXIXIIIIIIIIIIIIIIIIIIIIIIIIXXIXIIIXXIXIIIXXIXIIIIIIIIIIIIIIIIIIIIIII",
    "IIIIIIIIIIIIIIIXXIXIIIXXIXIIIXXIXIIIIIIIIIIIIIIIIIIIIIIIIXXIXIIIXXIXIIIXXIXIIIIIIIII",
    "IXXIXIIIIIIIIIIIIIIIIIIIIIIIIXXIXIIIXXIXIIIXXIXIIIIIIIIIIIIIIIIIIIIIIIIXXIXIIIXXIXII",
    "IXXIXIIIXXIXIIIXXIXIIIXXIXIIIXXIXIIIXXIXIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIII",
    "IIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIXXIXIIIXXIXIIIXXIXIIIXXIXIIIXXIXIIIXXIXII",
    "IIIIIIIIIIIIIIIZZIZIIIZZIZIIIZZIZIIIZZIZIIIIIIIIIIZZIZIIIIIIIIIIZZIZIIIIIIIIIIIIIIII",
    "IZZIZIIIIIIIIIIIIIIIIIIIIIIIIZZIZIIIIIIIIIIZZIZIIIZZIZIIIZZIZIIIIIIIIIIIIIIIIIZZIZII",
    "IZZIZIIIZZIZIIIZZIZIIIIIIIIIIIIIIIIIZZIZIIIZZIZIIIIIIIIIIIIIIIIIIIIIIIIZZIZIIIIIIIII",
    "IZZIZIIIIIIIIIIIIIIIIIZZIZIIIZZIZIIIZZIZIIIIIIIIIIIIIIIIIZZIZIIIIIIIIIIZZIZIIIIIIIII",
    "IIIIIIIIZZIZIIIZZIZIIIIIIIIIIIIIIIIIIIIIIIIZZIZIIIZZIZIIIIIIIIIIZZIZIIIIIIIIIIZZIZII"
]

stabs.extend(last_10)

pauli_stabs = [stim.PauliString(s) for s in stabs]

# Verify commutation
anticommuting = False
for i in range(len(pauli_stabs)):
    for j in range(i + 1, len(pauli_stabs)):
        if not pauli_stabs[i].commutes(pauli_stabs[j]):
            print(f"Anticommute: {i} vs {j}")
            anticommuting = True

if anticommuting:
    print("Failed: Stabilizers anticommute")
    # exit(1) 
    # Don't exit, try to generate anyway to see what happens, or maybe I should fix the last 10?
    # If last 10 fail, I need to know.

# print("Generating circuit...")

# Synthesize
try:
    # allow_underconstrained because we have 82 stabilizers for 84 qubits.
    tableau = stim.Tableau.from_stabilizers(pauli_stabs, allow_redundant=True, allow_underconstrained=True)
    circuit = tableau.to_circuit(method="graph_state")

    # Post-processing to remove resets and use H instead of RX
    final_circuit = stim.Circuit()
    for instruction in circuit:
        if instruction.name == "R":
            continue
        elif instruction.name == "RX":
            for t in instruction.targets_copy():
                final_circuit.append("H", [t])
        elif instruction.name == "RY":
            final_circuit.append("RY", instruction.targets_copy())
        else:
            final_circuit.append(instruction)

    print(final_circuit)
except Exception as e:
    print(f"Error: {e}")
