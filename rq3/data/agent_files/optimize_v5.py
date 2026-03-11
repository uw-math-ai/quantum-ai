import stim

def solve():
    print("Reading stabilizers...")
    with open("my_target_stabilizers_v5.txt", "r") as f:
        stabilizers = [line.strip() for line in f if line.strip()]

    print(f"Loaded {len(stabilizers)} stabilizers.")
    
    # Try to form a tableau from stabilizers
    try:
        # Prepend '+' to each stabilizer because stim expects sign
        # But wait, if they are just Pauli strings, stim might default to + or might require sign
        # stim.Tableau.from_stabilizers expects "string" arguments like "+XZ", "-YY"
        # The input has no signs. I will assume '+'.
        
        # Check if the input already has signs? No.
        
        # Also check for consistency
        # If I get an error, I might need allow_underconstrained=True
        
        stabs_ps = [stim.PauliString("+" + s) for s in stabilizers]
        
        print("Constructing tableau from stabilizers...")
        # Note: from_stabilizers returns a Tableau that maps Z basis to these stabilizers.
        t = stim.Tableau.from_stabilizers(stabs_ps, allow_underconstrained=True)
        
        print("Generating graph state circuit...")
        circuit = t.to_circuit(method="graph_state")
        
        print("Circuit generated.")
        
        clean_lines = []
        for instruction in circuit:
            if isinstance(instruction, stim.CircuitInstruction):
                name = instruction.name
                targets = instruction.targets_copy()
                
                if name == "R" or name == "RX" or name == "RY" or name == "RZ":
                    if name == "RX":
                        # RX resets to |+>. From |0>, this is H.
                        tgs = [t.value for t in targets]
                        clean_lines.append(f"H {' '.join(str(x) for x in tgs)}")
                    elif name == "R":
                        # Reset to |0>. From |0>, this is Identity.
                        pass
                    else:
                        print(f"Warning: Unexpected reset {name}")
                elif name == "M" or name == "MX" or name == "MY" or name == "MZ":
                    pass
                else:
                    # Convert to string and append
                    clean_lines.append(str(instruction))

        final_circuit_str = "\n".join(clean_lines)
        
        with open("candidate_graph.stim", "w") as f:
            f.write(final_circuit_str)
            
        print("Candidate written to candidate_graph.stim")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    solve()
