import stim

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
            # For non-H instructions, we must flush pending H on involved qubits
            targets = instruction.targets_copy()
            # Targets in Stim can be lookback/sweep but here we assume simple qubit indices
            # instruction.targets_copy() returns stim.GateTarget objects. t.value is the index.
            
            involved_qubits = set()
            for t in targets:
                if t.is_qubit_target:
                    involved_qubits.add(t.value)
            
            # Flush H for involved qubits
            # We can batch the H gates for efficiency/readability
            flushed_h = []
            for q in involved_qubits:
                if q in pending_h:
                    flushed_h.append(q)
                    pending_h.remove(q)
            
            if flushed_h:
                flushed_h.sort()
                new_circuit.append("H", flushed_h)
            
            new_circuit.append(instruction)
            
    # Flush remaining
    if pending_h:
        final_h = sorted(list(pending_h))
        new_circuit.append("H", final_h)
        
    return new_circuit

# Load candidate
with open("candidate_graph.stim", "r") as f:
    circuit = stim.Circuit(f.read())

optimized = optimize_circuit(circuit)

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

cx, vol = count_metrics(optimized)
print(f"Optimized Metrics: CX={cx}, Volume={vol}")

with open("candidate_optimized.stim", "w") as f:
    f.write(str(optimized))

# Check correctness again just to be sure
# Load stabilizers
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
sim.do(optimized)
preserved = 0
for stab in stabilizers:
    if sim.peek_observable_expectation(stim.PauliString(stab)) == 1:
        preserved += 1
print(f"Preserved: {preserved}/{len(stabilizers)}")

if preserved == len(stabilizers):
    print("Optimization VALID.")
else:
    print("Optimization INVALID.")
