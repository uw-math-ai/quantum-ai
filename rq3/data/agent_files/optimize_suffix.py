import stim

# Load the candidate
with open("optimized_candidate.stim", "r") as f:
    circuit = stim.Circuit(f.read())

# Find the split point
# The circuit has H layer, then CZ layer, then 1-qubit gates.
# The CZ layer is a single instruction with many targets in the file I wrote?
# Let's inspect the circuit structure.
# circuit[1] is the CZ instruction.
# circuit[2:] are the 1-qubit gates.

print("Original structure:")
for i, op in enumerate(circuit):
    print(f"{i}: {op}")

# Assume index 0 is H, index 1 is CZ.
# Verify this assumption.
if circuit[1].name == "CZ":
    prefix = stim.Circuit()
    prefix.append(circuit[0])
    prefix.append(circuit[1])
    
    suffix = stim.Circuit()
    for op in circuit[2:]:
        suffix.append(op)
        
    print("\nOptimizing suffix qubit by qubit...")
    
    # Group operations by qubit
    qubit_ops = {q: stim.Circuit() for q in range(12)}
    for op in suffix:
        for t in op.targets_copy():
            qubit_ops[t.value].append(op.name, [t.value])
            
    final_suffix = stim.Circuit()
    
    # We want to produce layers to minimize depth, but volume is additive.
    # So we just need minimal gate count per qubit.
    
    optimized_ops = []
    
    for q in range(12):
        if len(qubit_ops[q]) == 0:
            continue
            
        sim_q = stim.TableauSimulator()
        sim_q.do(qubit_ops[q])
        # We need the unitary. But TableauSimulator gives us the stabilizer map.
        # We can just use tableau.to_circuit() on this single qubit tableau!
        tab_q = sim_q.current_inverse_tableau().inverse()
        circ_q = tab_q.to_circuit()
        
        # Check if we can do better.
        # Stim's to_circuit for 1 qubit might be H S H S...
        # Let's trust it for now, it's usually decent.
        # But we can try to decompose it into standard gates if needed.
        
        for op in circ_q:
            optimized_ops.append(op)

    # Re-build the circuit from the list of operations
    # To keep it valid Stim, we can just append them.
    for op in optimized_ops:
        final_suffix.append(op)
        
    print("New qubit-wise suffix:")
    print(final_suffix)
    
    full_circuit = prefix + final_suffix
    
    with open("final_optimized.stim", "w") as f:
        f.write(str(full_circuit))
else:
    print("Structure assumption failed.")
