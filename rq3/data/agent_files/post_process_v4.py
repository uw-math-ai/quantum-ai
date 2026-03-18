import stim

# Read candidate.stim
with open("candidate.stim", "r") as f:
    circuit_text = f.read()

# Replace RX with H
# Since RX resets to |+>, and we assume |0> start, H is equivalent.
# Simple string replacement is risky if RX is not at start or has args.
# But graph state synthesis puts RX at start.
# Let's use stim to be safe.

circuit = stim.Circuit(circuit_text)
new_circuit = stim.Circuit()

for instr in circuit:
    if instr.name == "RX":
        # RX initializes to |+>. Since start is |0>, use H.
        # instr.targets_copy() might be needed for older stim
        try:
            targets = instr.targets_copy()
        except AttributeError:
            # Fallback for newer stim? Or older?
            # In newer stim, instr.targets is a property returning list.
            targets = instr.targets
            
        # Add H on all targets
        for t in targets:
            new_circuit.append("H", [t])
            
    elif instr.name == "TICK":
        pass
        
    else:
        # Keep everything else (including CZ)
        new_circuit.append(instr)

with open("candidate_optimized.stim", "w") as f:
    f.write(str(new_circuit))
    
print("Saved candidate_optimized.stim with CZ preserved.")
