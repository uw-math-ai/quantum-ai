import stim

# Load optimized circuit
with open("optimized_circuit.stim", "r") as f:
    circuit = stim.Circuit(f.read())

# Fix circuit: RX -> H
new_circuit = stim.Circuit()
for instr in circuit:
    if instr.name == "RX":
        new_circuit.append("H", instr.targets_copy())
    elif instr.name in ["R", "RZ"]:
        pass # Identity
    else:
        new_circuit.append(instr)

# Save final
with open("final.stim", "w") as f:
    f.write(str(new_circuit))

# Load fixed stabilizers
with open("fixed_stabilizers.txt", "r") as f:
    stabs = [stim.PauliString(l.strip().replace(',', '')) for l in f if l.strip()]

# Check
s = stim.TableauSimulator()
s.do(new_circuit)
preserved = 0
for stab in stabs:
    if s.peek_observable_expectation(stab) == 1:
        preserved += 1

print(f"Preserved {preserved}/{len(stabs)}")
if preserved == len(stabs):
    print("VALID")
else:
    print("INVALID")
    # Debug
    for i, stab in enumerate(stabs):
        if s.peek_observable_expectation(stab) != 1:
            print(f"Failed {i}: {stab}")
            break
