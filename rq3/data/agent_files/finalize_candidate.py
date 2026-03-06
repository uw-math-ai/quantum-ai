import stim

# Load optimized candidate
with open("candidate_optimized.stim", "r") as f:
    circuit = stim.Circuit(f.read())

new_circuit = stim.Circuit()
for inst in circuit:
    if inst.name == "RX":
        # Replace RX with H
        new_circuit.append("H", inst.targets_copy())
    elif inst.name == "TICK":
        continue
    else:
        new_circuit.append(inst)

# Now run H-cancellation again
def optimize_circuit(circuit):
    new_circuit = stim.Circuit()
    pending_h = set()
    
    for instruction in circuit:
        if instruction.name == "H":
            for t in instruction.targets_copy():
                q = t.value
                if q in pending_h:
                    pending_h.remove(q)
                else:
                    pending_h.add(q)
        else:
            involved_qubits = set()
            for t in instruction.targets_copy():
                if t.is_qubit_target:
                    involved_qubits.add(t.value)
            
            flushed_h = []
            for q in involved_qubits:
                if q in pending_h:
                    flushed_h.append(q)
                    pending_h.remove(q)
            
            if flushed_h:
                flushed_h.sort()
                new_circuit.append("H", flushed_h)
            
            new_circuit.append(instruction)
            
    if pending_h:
        final_h = sorted(list(pending_h))
        new_circuit.append("H", final_h)
        
    return new_circuit

final_circuit = optimize_circuit(new_circuit)

# Count metrics
def count_metrics(circ):
    cx_count = 0
    volume = 0
    for inst in circ:
        if inst.name == "CX":
            n = len(inst.targets_copy()) // 2
            cx_count += n
            volume += n
        elif inst.name in ["H", "S", "S_DAG", "X", "Y", "Z", "SQRT_X", "SQRT_X_DAG", "SQRT_Y", "SQRT_Y_DAG", "XCZ", "YCX"]:
             volume += len(inst.targets_copy())
    return cx_count, volume

cx, vol = count_metrics(final_circuit)
print(f"Final Metrics: CX={cx}, Volume={vol}")

with open("candidate_final.stim", "w") as f:
    f.write(str(final_circuit))

# Verify preservation one last time
stabilizers_str = """
XZZXIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIII
IIIIIXZZXIIIIIIIIIIIIIIIIIIIIIIIIIIIIIII
IIIIIIIIIIXZZXIIIIIIIIIIIIIIIIIIIIIIIIII
IIIIIIIIIIIIIIIXZZXIIIIIIIIIIIIIIIIIIIII
IIIIIIIIIIIIIIIIIIIIXZZXIIIIIIIIIIIIIIII
IIIIIIIIIIIIIIIIIIIIIIIIIXZZXIIIIIIIIIII
IIIIIIIIIIIIIIIIIIIIIIIIIIIIIIXZZXIIIIII
IIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIXZZXI
IXZZXIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIII
IIIIIIXZZXIIIIIIIIIIIIIIIIIIIIIIIIIIIIII
IIIIIIIIIIIXZZXIIIIIIIIIIIIIIIIIIIIIIIII
IIIIIIIIIIIIIIIIXZZXIIIIIIIIIIIIIIIIIIII
IIIIIIIIIIIIIIIIIIIIIXZZXIIIIIIIIIIIIIII
IIIIIIIIIIIIIIIIIIIIIIIIIIXZZXIIIIIIIIII
IIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIXZZXIIIII
IIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIXZZX
XIXZZIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIII
IIIIIXIXZZIIIIIIIIIIIIIIIIIIIIIIIIIIIIII
IIIIIIIIIIXIXZZIIIIIIIIIIIIIIIIIIIIIIIII
IIIIIIIIIIIIIIIXIXZZIIIIIIIIIIIIIIIIIIII
IIIIIIIIIIIIIIIIIIIIXIXZZIIIIIIIIIIIIIII
IIIIIIIIIIIIIIIIIIIIIIIIIXIXZZIIIIIIIIII
IIIIIIIIIIIIIIIIIIIIIIIIIIIIIIXIXZZIIIII
IIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIXIXZZ
ZXIXZIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIII
IIIIIZXIXZIIIIIIIIIIIIIIIIIIIIIIIIIIIIII
IIIIIIIIIIZXIXZIIIIIIIIIIIIIIIIIIIIIIIII
IIIIIIIIIIIIIIIZXIXZIIIIIIIIIIIIIIIIIIII
IIIIIIIIIIIIIIIIIIIIZXIXZIIIIIIIIIIIIIII
IIIIIIIIIIIIIIIIIIIIIIIIIZXIXZIIIIIIIIII
IIIIIIIIIIIIIIIIIIIIIIIIIIIIIIZXIXZIIIII
IIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIZXIXZ
XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
ZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZ
"""
stabilizers = [line.strip() for line in stabilizers_str.splitlines() if line.strip()]

sim = stim.TableauSimulator()
sim.do(final_circuit)
preserved = 0
for stab in stabilizers:
    if sim.peek_observable_expectation(stim.PauliString(stab)) == 1:
        preserved += 1
print(f"Preserved: {preserved}/{len(stabilizers)}")
