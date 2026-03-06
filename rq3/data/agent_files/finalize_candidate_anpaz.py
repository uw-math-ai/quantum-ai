
import stim

with open("candidate.stim", "r") as f:
    circuit = stim.Circuit(f.read())

new_circuit = stim.Circuit()
for instr in circuit:
    if instr.name == "RX":
        new_circuit.append("H", instr.targets_copy())
    elif instr.name == "TICK":
        pass
    else:
        new_circuit.append(instr)

with open("candidate_final.stim", "w") as f:
    f.write(str(new_circuit))

print("Finalized circuit saved to candidate_final.stim")
