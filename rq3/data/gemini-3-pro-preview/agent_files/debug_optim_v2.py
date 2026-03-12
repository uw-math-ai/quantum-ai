import stim

with open("candidate.stim", "r") as f:
    circuit = stim.Circuit(f.read())

print(f"Total instructions: {len(circuit)}")

seen_cz = False
for i, instr in enumerate(circuit):
    # Only print first few and last few if too many
    if i < 5 or i > len(circuit) - 5:
        print(f"Instr {i}: {instr.name} targets={len(instr.targets_copy())}")
        if instr.name == "CZ":
            seen_cz = True
        elif instr.name == "H" and not seen_cz:
            print("  -> Initial H layer")
        elif seen_cz:
            print("  -> Accumulating SQ")
            # Check if it acts on qubit 0
            for t in instr.targets_copy():
                if t.value == 0:
                    print("     !!! Acting on qubit 0 !!!")
    elif i == 5:
        print("...")
        if instr.name == "CZ":
            seen_cz = True
