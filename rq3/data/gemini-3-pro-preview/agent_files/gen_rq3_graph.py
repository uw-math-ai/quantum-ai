import stim

def generate_graph_state():
    # Read stabilizers
    with open("target_stabilizers_rq3_fresh.txt", "r") as f:
        lines = [l.strip() for l in f if l.strip()]
    
    # Clean up lines and enforce length 42
    cleaned_lines = []
    for line in lines:
        parts = line.split(',')
        for p in parts:
            if p.strip():
                s = p.strip()
                # Truncate to 42 since max used is 41
                if len(s) > 42:
                    s = s[:42]
                cleaned_lines.append(s)
    
    stabilizers = [stim.PauliString(s) for s in cleaned_lines]
    
    # Synthesize
    try:
        # allow_redundant=True because usually provided stabilizers are generators but might have redundancy
        # allow_underconstrained=True in case they don't specify full state (though for graph state usually we want full)
        tableau = stim.Tableau.from_stabilizers(stabilizers, allow_redundant=True, allow_underconstrained=True)
        circuit = tableau.to_circuit(method="graph_state")
        
        # Post-process to match baseline expectations
        # 1. Remove explicit resets (R, RX, RY, RZ) if we assume input is |0>
        # 2. Convert RX (reset X) to H if input is |0> (since RX prepares |+>, and H|0> = |+>)
        
        new_circuit = stim.Circuit()
        for instr in circuit:
            if instr.name == "RX":
                # RX resets to |+>. If input is |0>, H does that.
                # However, if it's in the middle of circuit, it's a reset.
                # Usually graph_state puts these at start.
                new_circuit.append("H", instr.targets_copy())
            elif instr.name == "R":
                # R resets to |0>. If input is |0>, this is identity.
                pass
            elif instr.name == "M":
                # Measurements not allowed unless in baseline.
                pass 
            else:
                new_circuit.append(instr)
        
        # Generate list of strings to avoid Stim auto-merging or formatting issues
        circuit_lines = []
        for instr in new_circuit:
            if len(instr.targets_copy()) > 10:
                targets = instr.targets_copy()
                name = instr.name
                
                if name == "CZ" or name == "CX" or name == "SWAP":
                    # 2-qubit gates
                    for i in range(0, len(targets), 2):
                        chunk = targets[i:i+2]
                        # Convert targets to string manually
                        t_str = " ".join(str(t.value) for t in chunk)
                        circuit_lines.append(f"{name} {t_str}")
                else:
                    # 1-qubit gates
                    for i in range(0, len(targets), 10):
                         chunk = targets[i:i+10]
                         t_str = " ".join(str(t.value) for t in chunk)
                         circuit_lines.append(f"{name} {t_str}")
            else:
                circuit_lines.append(str(instr))
        
        with open("candidate_split_manual.stim", "w") as f:
            for line in circuit_lines:
                f.write(line + "\n")
        print("Written to candidate_split_manual.stim")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    generate_graph_state()
