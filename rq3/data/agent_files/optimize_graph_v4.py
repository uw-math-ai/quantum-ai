import stim
import sys

def main():
    try:
        with open("my_baseline_task.stim", "r") as f:
            baseline_text = f.read()
        circuit = stim.Circuit(baseline_text)
    except Exception as e:
        print(f"Error loading baseline: {e}")
        return

    # Tableau from circuit
    tableau = stim.Tableau.from_circuit(circuit)

    # Graph state circuit
    graph_circuit = tableau.to_circuit(method="graph_state")

    # Clean resets and split lines
    clean_circuit = stim.Circuit()
    
    for instruction in graph_circuit:
        if instruction.name == "RX":
            # Convert RX t1 t2 to H t1 H t2
            # Split into individual H gates to be safe
            for t in instruction.targets_copy():
                clean_circuit.append("H", [t])
        elif instruction.name in ["R", "RZ"]:
            pass 
        else:
            # Check number of targets
            targets = instruction.targets_copy()
            name = instruction.name
            args = instruction.gate_args_copy()
            
            # Simple gates with no args
            if not args:
                if name in ["CX", "CZ", "SWAP"]:
                    # 2-qubit gates. Process in pairs.
                    # chunks of 3 pairs (6 targets)
                    chunk_size = 6
                    for i in range(0, len(targets), chunk_size):
                        chunk = targets[i:i+chunk_size]
                        clean_circuit.append(name, chunk)
                else:
                    # 1-qubit gates usually (or others). 
                    # chunks of 5 targets
                    chunk_size = 5
                    for i in range(0, len(targets), chunk_size):
                        chunk = targets[i:i+chunk_size]
                        clean_circuit.append(name, chunk)
            else:
                # Gates with args, just keep them (usually rare/short in graph state)
                clean_circuit.append(instruction)

    # Write
    with open("candidate_split.stim", "w") as f:
        f.write(str(clean_circuit))

    print("Candidate generated in candidate_split.stim")

if __name__ == "__main__":
    main()
