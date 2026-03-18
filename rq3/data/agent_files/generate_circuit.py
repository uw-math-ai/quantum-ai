import stim

stabilizers = [
    "XZZXIIIIIIIIIIIIIIIIIIIIIIIIIIIIIII", "IIIIIXZZXIIIIIIIIIIIIIIIIIIIIIIIIII", "IIIIIIIIIIXZZXIIIIIIIIIIIIIIIIIIIII", "IIIIIIIIIIIIIIIXZZXIIIIIIIIIIIIIIII", "IIIIIIIIIIIIIIIIIIIIXZZXIIIIIIIIIII", "IIIIIIIIIIIIIIIIIIIIIIIIIXZZXIIIIII", "IIIIIIIIIIIIIIIIIIIIIIIIIIIIIIXZZXI", "IXZZXIIIIIIIIIIIIIIIIIIIIIIIIIIIIII", "IIIIIIXZZXIIIIIIIIIIIIIIIIIIIIIIIII", "IIIIIIIIIIIXZZXIIIIIIIIIIIIIIIIIIII", "IIIIIIIIIIIIIIIIXZZXIIIIIIIIIIIIIII", "IIIIIIIIIIIIIIIIIIIIIXZZXIIIIIIIIII", "IIIIIIIIIIIIIIIIIIIIIIIIIIXZZXIIIII", "IIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIXZZX", "XIXZZIIIIIIIIIIIIIIIIIIIIIIIIIIIIII", "IIIIIXIXZZIIIIIIIIIIIIIIIIIIIIIIIII", "IIIIIIIIIIXIXZZIIIIIIIIIIIIIIIIIIII", "IIIIIIIIIIIIIIIXIXZZIIIIIIIIIIIIIII", "IIIIIIIIIIIIIIIIIIIIXIXZZIIIIIIIIII", "IIIIIIIIIIIIIIIIIIIIIIIIIXIXZZIIIII", "IIIIIIIIIIIIIIIIIIIIIIIIIIIIIIXIXZZ", "ZXIXZIIIIIIIIIIIIIIIIIIIIIIIIIIIIII", "IIIIIZXIXZIIIIIIIIIIIIIIIIIIIIIIIII", "IIIIIIIIIIZXIXZIIIIIIIIIIIIIIIIIIII", "IIIIIIIIIIIIIIIZXIXZIIIIIIIIIIIIIII", "IIIIIIIIIIIIIIIIIIIIZXIXZIIIIIIIIII", "IIIIIIIIIIIIIIIIIIIIIIIIIZXIXZIIIII", "IIIIIIIIIIIIIIIIIIIIIIIIIIIIIIZXIXZ", "XXXXXXXXXXXXXXXXXXXXIIIIIIIIIIIIIII", "XXXXXIIIIIXXXXXIIIIIXXXXXIIIIIXXXXX", "IIIIIIIIIIXXXXXXXXXXXXXXXXXXXXIIIII", "ZZZZZZZZZZZZZZZZZZZZIIIIIIIIIIIIIII", "ZZZZZIIIIIZZZZZIIIIIZZZZZIIIIIZZZZZ", "IIIIIIIIIIZZZZZZZZZZZZZZZZZZZZIIIII"
]

def synthesize_and_print():
    try:
        # Create tableau from stabilizers
        tableau = stim.Tableau.from_stabilizers([stim.PauliString(s) for s in stabilizers], allow_underconstrained=True)
        
        # Method 1: Graph State
        circuit_graph = tableau.to_circuit(method="graph_state")
        
        # Replace RX with H
        new_circuit = stim.Circuit()
        for instr in circuit_graph:
            if instr.name == "RX":
                # Replace RX targets with H
                new_circuit.append("H", instr.targets_copy())
            elif instr.name == "TICK":
                continue
            else:
                new_circuit.append(instr)
        
        with open("candidate.stim", "w") as f:
            for instr in new_circuit:
                # Print instruction name
                f.write(instr.name)
                # Print targets
                for target in instr.targets_copy():
                    f.write(f" {target.value}")
                f.write("\n")
            
        print(f"Generated candidate.stim with {len(new_circuit)} instructions.")
        print(f"CX count: {new_circuit.num_2qubit_gates() if 'CX' in str(new_circuit) else 0}") # Rough check
        # Actually num_2qubit_gates counts CZ too.
        cx = sum(1 for op in new_circuit if op.name == "CX")
        cz = sum(1 for op in new_circuit if op.name == "CZ")
        print(f"CX count: {cx}")
        print(f"CZ count: {cz}")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    synthesize_and_print()
