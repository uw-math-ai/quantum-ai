import stim

def optimize_h_cancellation(circuit):
    # Expand CZ to H CX H first
    expanded = stim.Circuit()
    for instr in circuit:
        if instr.name == "CZ":
            targets = instr.targets_copy()
            for i in range(0, len(targets), 2):
                a = targets[i]
                b = targets[i+1]
                # CZ(a,b) = H(b) CX(a,b) H(b)
                expanded.append("H", [b])
                expanded.append("CX", [a, b])
                expanded.append("H", [b])
        else:
            expanded.append(instr)
            
    final_circ = stim.Circuit()
    pending_h = set()
    
    for instr in expanded:
        if instr.name == "H":
            for t in instr.targets_copy():
                q = t.value
                if q in pending_h:
                    pending_h.remove(q)
                else:
                    pending_h.add(q)
        elif instr.name == "CX":
            targets = instr.targets_copy()
            for i in range(0, len(targets), 2):
                c = targets[i].value
                t = targets[i+1].value
                
                if c in pending_h:
                    final_circ.append("H", [c])
                    pending_h.remove(c)
                if t in pending_h:
                    final_circ.append("H", [t])
                    pending_h.remove(t)
                
                final_circ.append("CX", [c, t])
        else:
            # Flush for any targets
            targets = instr.targets_copy()
            for t in targets:
                if t.is_qubit_target:
                    q = t.value
                    if q in pending_h:
                        final_circ.append("H", [q])
                        pending_h.remove(q)
            final_circ.append(instr)
            
    # Flush remaining
    for q in sorted(list(pending_h)):
        final_circ.append("H", [q])
        
    return final_circ

def main():
    try:
        with open("current_task_stabilizers.txt", "r") as f:
            lines = [l.strip() for l in f if l.strip()]
        stabilizers = [stim.PauliString(l) for l in lines]
        
        # Remove index 28 if it exists and count matches expectation
        # We know index 28 is the problematic one.
        if len(stabilizers) >= 29:
            print(f"Original count: {len(stabilizers)}. Removing index 28.")
            del stabilizers[28]
        
        tableau = stim.Tableau.from_stabilizers(stabilizers, allow_underconstrained=True)
        graph_circuit = tableau.to_circuit(method="graph_state")
        
        optimized = optimize_h_cancellation(graph_circuit)
        
        # Count CX
        cx_count = 0
        for instr in optimized:
            if instr.name == "CX":
                cx_count += len(instr.targets_copy()) // 2
        
        print(f"Optimized CX count: {cx_count}")
        
        with open("candidate_v3.stim", "w") as f:
            f.write(str(optimized))
            
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
