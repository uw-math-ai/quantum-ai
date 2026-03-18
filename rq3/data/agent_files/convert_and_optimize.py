import stim

def optimize_circuit(circuit):
    # Simple peephole optimization: remove adjacent inverse gates
    # Since we only introduce H, we look for H followed by H
    
    new_instructions = []
    
    # First pass: Replace RX with H, and Expand CZ to CX
    expanded_circuit = stim.Circuit()
    for instruction in circuit:
        if instruction.name == "RX":
            # Replace RX with H, assuming input |0>
            expanded_circuit.append("H", instruction.targets_copy())
        elif instruction.name == "CZ":
            targets = instruction.targets_copy()
            # Iterate pairs
            for i in range(0, len(targets), 2):
                c = targets[i]
                t = targets[i+1]
                # CZ(c, t) = H(t) CX(c, t) H(t)
                expanded_circuit.append("H", [t])
                expanded_circuit.append("CX", [c, t])
                expanded_circuit.append("H", [t])
        else:
            expanded_circuit.append(instruction)
            
    # Second pass: Cancel adjacent H gates
    # We reconstruct the circuit
    optimized_circuit = stim.Circuit()
    # We can process the circuit and buffer H gates
    
    # State tracking is hard.
    # Let's do a simple list-based cancellation.
    # Convert to list of (name, targets)
    ops = []
    for instr in expanded_circuit:
        # Decompose multi-target ops for easier processing? 
        # Actually, H is single target. CX is double.
        # Let's flatten everything to single-op-per-instruction
        name = instr.name
        targets = instr.targets_copy()
        
        if name in ["CX", "CNOT", "CZ", "SWAP"]:
            # 2 qubit gates
            for i in range(0, len(targets), 2):
                ops.append((name, targets[i:i+2]))
        elif name in ["H", "S", "X", "Y", "Z", "I", "SQRT_X", "SQRT_Y", "SQRT_Z", "S_DAG", "SQRT_X_DAG", "SQRT_Y_DAG", "SQRT_Z_DAG"]:
            # 1 qubit gates
            for t in targets:
                ops.append((name, [t]))
        else:
            # TICK or other
            ops.append((name, targets))
            
    # Now iterate and cancel H-H
    # We need to track dependencies. This is getting complex for a script.
    # Simpler heuristic: 
    # Just iterate through ops. If we see H(q) and immediately previous op on q was H, remove.
    # We need to track "last op on qubit q".
    
    final_ops = []
    # last_op_idx[q] = index in final_ops
    # But checking if they are adjacent is tricky with other qubits.
    # "Adjacent" means no other gate touched q in between.
    
    # Let's stick to the expanded circuit. 592 CX is already winning.
    # Volume reduction is secondary.
    # I'll just return the expanded circuit (with RX->H) to be safe.
    # The complexity of writing a correct optimizer in one shot is high.
    # I don't want to risk invalidating the circuit.
    
    return expanded_circuit

def count_metrics(circuit):
    cx = 0
    vol = 0
    for instruction in circuit:
        name = instruction.name
        n_targets = len(instruction.targets_copy())
        
        if name in ["CX", "CNOT"]:
            cx += n_targets // 2
            
        if name in ["CX", "CNOT", "CY", "CZ", "SWAP", "ISWAP", "ISWAP_DAG"]:
            vol += n_targets // 2
        else:
            vol += n_targets
            
    return cx, vol

def check_stabilizers(circuit, stabilizers):
    sim = stim.TableauSimulator()
    sim.do(circuit)
    
    preserved = True
    for stab_str in stabilizers:
        pauli = stim.PauliString(stab_str)
        if sim.peek_observable_expectation(pauli) != 1:
            preserved = False
            break
            
    return preserved

def main():
    try:
        with open("candidate_graph.stim", "r") as f:
            graph_circuit = stim.Circuit(f.read())
            
        print("Loaded candidate_graph.stim")
        
        # Optimize/Convert
        final_circuit = optimize_circuit(graph_circuit)
        
        # Check metrics
        cx, vol = count_metrics(final_circuit)
        print(f"Converted Metrics: CX={cx}, Vol={vol}")
        
        # Check stabilizers
        stabilizers = []
        with open("current_task_stabilizers.txt", "r") as f:
            for line in f:
                line = line.strip()
                if line:
                    stabilizers.append(line)
                    
        valid = check_stabilizers(final_circuit, stabilizers)
        print(f"Converted Valid: {valid}")
        
        if valid:
            with open("candidate_cx.stim", "w") as f:
                f.write(str(final_circuit))
            print("Saved candidate_cx.stim")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
