import stim

stabilizers = [
    "XXXIIIXXXIII",
    "IIXXXIIIXXXI",
    "XIIIXXXIIIXX",
    "XXXXXIIIIII", # This one is length 11. Let's see if baseline satisfies it with I or X at end.
    "IIIIIIXXXXXX",
    "IIZZZZIZIZII",
    "ZIIIZIZZZIIZ",
    "ZZZIIZZIIIZI",
    "ZIIZZZIIZIZI",
    "IZZIIIZZIZIZ"
]

# Load baseline
with open("baseline.stim", "r") as f:
    circuit = stim.Circuit(f.read())

sim = stim.TableauSimulator()
sim.do(circuit)

print(f"Num qubits: {circuit.num_qubits}")

for i, stab in enumerate(stabilizers):
    # Pad to 12 chars if necessary
    if len(stab) < 12:
        print(f"Warning: Stabilizer {i} '{stab}' has length {len(stab)}.")
        # Try both 'I' and 'X' and 'Z'?
        # Let's just create a PauliString and see what the simulator says.
        # But we need to know the target.
        pass
    
    # Construct PauliString
    # If length is 11, we need to guess the 12th char.
    # Given the others are 12, it's likely 12.
    
    candidates = []
    if len(stab) == 11:
         candidates = [stab + "I", stab + "X", stab + "Z", stab + "Y"]
    else:
         candidates = [stab]
         
    found = False
    for cand in candidates:
        try:
            p = stim.PauliString(cand)
            if sim.peek_observable_expectation(p) == 1:
                print(f"Stabilizer {i} preserved as {cand}")
                found = True
                break
        except Exception as e:
            print(f"Error checking {cand}: {e}")
            
    if not found:
        print(f"Stabilizer {i} NOT preserved (tried {candidates})")

print("Baseline stabilizers:")
print(sim.canonical_stabilizers())

