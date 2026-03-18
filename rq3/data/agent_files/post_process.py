import stim

with open("synthesized.stim", "r") as f:
    circuit_text = f.read()

circuit = stim.Circuit(circuit_text)

new_circuit = stim.Circuit()

for instr in circuit:
    if instr.name == "RX":
        # RX initializes to |+>. Since start is |0>, use H.
        targets = instr.targets_copy()
        new_circuit.append("H", targets)
    elif instr.name == "CZ":
        # Decompose CZ p q -> H q, CX p q, H q
        targets = instr.targets_copy()
        for i in range(0, len(targets), 2):
            t1 = targets[i]
            t2 = targets[i+1]
            # t1 and t2 are GateTarget objects. pass them directly.
            new_circuit.append("H", [t2])
            new_circuit.append("CX", [t1, t2])
            new_circuit.append("H", [t2])
    elif instr.name == "TICK":
        pass
    else:
        # Keep other instructions (H, S, X, Y, Z, etc.)
        new_circuit.append(instr)

with open("final_candidate.stim", "w") as f:
    f.write(str(new_circuit))

print("Post-processing complete.")
