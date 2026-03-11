import stim
import re
import sys

def count_cx(circuit):
    count = 0
    for instr in circuit:
        if instr.name == "CX" or instr.name == "CNOT":
            count += len(instr.targets) // 2
    return count

def generate_circuit():
    # Load stabilizers
    with open("current_target_stabilizers.txt", "r") as f:
        content = f.read().strip()
    
    # Split by comma or newline
    lines = re.split(r'[,\n]+', content)
    # Filter empty strings and whitespace
    lines = [l.strip() for l in lines if l.strip()]
    
    try:
        # Create Tableau from stabilizers
        tableau = stim.Tableau.from_stabilizers([stim.PauliString(s) for s in lines])
    except Exception as e:
        print(f"Error creating tableau: {e}")
        return None

    # Synthesize circuit
    # method="graph_state" is usually optimal for 2-qubit gates (CZ)
    circ = tableau.to_circuit(method="graph_state")
    
    # Post-process to remove resets and convert to CX
    new_circ = stim.Circuit()
    
    for instr in circ:
        if instr.name == "R" or instr.name == "RY":
            # Remove resets (assuming start state is |0>)
            pass
        elif instr.name == "RX":
            # Replace RX with H (RX resets to |+>, so from |0> we need H)
            for t in instr.targets:
                new_circ.append("H", [t])
        elif instr.name == "CZ":
            # Convert CZ to CX: H t, CX c t, H t
            # Note: CZ is symmetric, so target/control doesn't matter for logic,
            # but for optimization, maybe it does? 
            # We'll just pick one.
            for i in range(0, len(instr.targets), 2):
                c = instr.targets[i]
                t = instr.targets[i+1]
                new_circ.append("H", [t])
                new_circ.append("CX", [c, t])
                new_circ.append("H", [t])
        else:
             new_circ.append(instr)
             
    # Optimization: Simple peephole to cancel adjacent H gates
    # This reduces the H count added by CZ decomposition.
    
    # We'll convert to a list of operations to process
    ops = []
    for instr in new_circ:
        if instr.name in ["H", "S", "X", "Y", "Z", "I"]:
            for t in instr.targets:
                ops.append({"name": instr.name, "targets": [t.value]})
        elif instr.name in ["CX", "CZ", "SWAP"]:
            for i in range(0, len(instr.targets), 2):
                ops.append({"name": instr.name, "targets": [instr.targets[i].value, instr.targets[i+1].value]})
        else:
            # Keep others as is (e.g. measurements, though we shouldn't have any)
            ops.append({"name": instr.name, "targets": [t.value for t in instr.targets], "raw": instr})

    # Optimization pass
    # We iterate and build a new list. 
    # If we see H acting on qubit q, and the previous op on q was H, remove both.
    # This requires tracking the "frontier" of each qubit.
    # This is non-trivial to implement perfectly in a short script.
    
    # Let's use a simpler heuristic:
    # Just look for immediate neighbors in the list? No, gates on other qubits might intervene.
    
    # Better approach: Use stim's own fusion if available? No.
    # Let's write a "cancellation" pass.
    
    final_ops = []
    # Track the last operation index for each qubit
    # qubit_last_op_index = {} 
    # This is complex because multi-qubit gates entangle.
    
    # ALTERNATIVE: Just output the circuit as is. 
    # The CZ -> CX conversion adds 2 H per CZ.
    # If we have many CZs, this is costly in volume.
    # But usually "graph state" circuits are efficient.
    
    # Let's try to do a safe cancellation:
    # If we have [H q], [H q] with NOTHING involving q in between, we cancel.
    
    # We can do this by maintaining a "pending H" set for each qubit?
    # No, order matters.
    
    # Simplest:
    # Iterate through ops.
    # Maintain a "stack" of gates for each qubit?
    # No, just let Stim do it? Stim doesn't have "optimize" method exposed in Python easily.
    
    # Let's try to cancel immediate H-H if they are adjacent in the list (ignoring other qubits).
    # But we have to be careful about commutation.
    # Actually, if we just synthesized it, the structure is:
    # H on some qubits
    # CZs
    # H on some qubits (maybe)
    # S, X, etc.
    
    # The CZ decomposition:
    # H t
    # CX c t
    # H t
    
    # If we have multiple CZs involving `t`, we get:
    # ...
    # H t
    # CX c1 t
    # H t
    # H t  <-- from next CZ
    # CX c2 t
    # H t
    # ...
    # The H t, H t in the middle CANCEL!
    
    # So yes, we definitely want to cancel adjacent H's on the same qubit.
    # Since we are generating the sequence, we can just buffer the H's.
    
    optimized_circ = stim.Circuit()
    
    # We will process the circuit we generated `new_circ`
    # We can't easily cancel across other gates without dependency analysis.
    # But in graph state circuits, we often have blocks of CZs.
    # The `to_circuit` output groups them.
    
    # Let's try a greedy approach:
    # Build the circuit, but whenever we add a gate, check if it cancels the previous gate on that qubit?
    # Too hard.
    
    # Let's just output the circuit with H-CX-H.
    # BUT, we can optimize the generated list.
    # If we see [H t], [H t], we remove both.
    # We need to ensure no gate involving t is between them.
    
    # Let's iterate through the ops.
    # We maintain a list of "active" operations.
    # When adding an op, we check if it commutes with everything since the last op on its qubits.
    # That's too complex.
    
    # Let's just stick to the simple "graph state" output.
    # If `cx_count` is the metric, converting CZ to CX yields 1 CX.
    # So `cx_count` = number of CZs.
    # The Baseline has lots of CX.
    # Graph state synthesis minimizes interaction.
    # It might be optimal.
    
    return new_circ

if __name__ == "__main__":
    c = generate_circuit()
    if c:
        # Save to candidate.stim
        c.to_file("candidate.stim")
        print(f"Generated candidate with {count_cx(c)} CX gates.")
        
        # Check baseline
        with open("current_baseline.stim") as f:
            base = stim.Circuit(f.read())
        print(f"Baseline has {count_cx(base)} CX gates.")
