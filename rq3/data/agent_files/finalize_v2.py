import stim
import sys

def get_metrics(circuit):
    cx = 0
    vol = 0
    for instruction in circuit:
        if instruction.name in ["TICK", "SHIFT_COORDS", "QUBIT_COORDS", "DETECTOR", "OBSERVABLE_INCLUDE"]:
            continue
            
        n_targets = len(instruction.targets_copy())
        if instruction.name in ["CX", "CNOT"]:
            count = n_targets // 2
            vol += count
            cx += count
        elif instruction.name in ["CY", "CZ", "SWAP", "ISWAP", "ISWAP_DAG"]:
            count = n_targets // 2
            vol += count
        else:
             vol += n_targets
    return cx, vol

# Load best candidate
try:
    with open("best_candidate.stim", "r") as f:
        circuit_text = f.read()
except FileNotFoundError:
    print("best_candidate.stim not found")
    sys.exit(1)

circuit = stim.Circuit(circuit_text)
new_circuit = stim.Circuit()

# Process instructions
for instruction in circuit:
    if instruction.name == "RX":
        # Replace RX with H (state |0> -> |+>)
        for t in instruction.targets_copy():
            new_circuit.append("H", [t])
    elif instruction.name == "R" or instruction.name == "RZ":
        # Remove R (Reset Z) as it is Identity on |0>
        pass
    elif instruction.name == "RY":
        # Replace RY with H then S (state |0> -> |i>)
        for t in instruction.targets_copy():
            new_circuit.append("H", [t])
            new_circuit.append("S", [t])
    elif instruction.name == "MX" or instruction.name == "MY" or instruction.name == "MZ" or instruction.name == "M":
        pass
    else:
        new_circuit.append(instruction)

# Save final
with open("final.stim", "w") as f:
    f.write(str(new_circuit))

# Verify metrics
cx, vol = get_metrics(new_circuit)
print(f"Final Circuit Metrics: CX={cx}, Vol={vol}")

# Load stabilizers
try:
    with open("stabilizers.txt", "r") as f:
        stabilizers = [stim.PauliString(line.strip()) for line in f if line.strip()]
except FileNotFoundError:
    print("stabilizers.txt not found")
    sys.exit(1)

# Check preservation using TableauSimulator
sim = stim.TableauSimulator()
sim.do(new_circuit)

preserved = 0
for s in stabilizers:
    val = sim.peek_observable_expectation(s)
    if val == 1:
        preserved += 1
    # else print nothing to keep output clean unless debugging

print(f"Preserved Stabilizers: {preserved}/{len(stabilizers)}")

if preserved == len(stabilizers):
    print("VALID: All stabilizers preserved.")
else:
    print("INVALID: Some stabilizers not preserved.")
