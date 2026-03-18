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

    tableau = stim.Tableau.from_circuit(circuit)
    graph_circuit = tableau.to_circuit(method="graph_state")

    output_lines = []
    
    for instruction in graph_circuit:
        name = instruction.name
        targets = instruction.targets_copy()
        args = instruction.gate_args_copy()
        
        if name == "RX":
            # Convert to individual H gates
            for t in targets:
                # t is GateTarget. value gives index.
                output_lines.append(f"H {t.value}")
        elif name in ["R", "RZ"]:
            pass
        elif name == "TICK":
            output_lines.append("TICK")
        else:
            # Process generic gates
            # Convert targets to integers
            t_vals = [t.value for t in targets]
            
            # Decide chunk size
            if name in ["CX", "CZ", "SWAP", "CNOT"]:
                chunk_size = 6 # 3 pairs
            else:
                chunk_size = 5 # 5 single qubits

            if not args:
                for i in range(0, len(t_vals), chunk_size):
                    chunk = t_vals[i:i+chunk_size]
                    line = f"{name} " + " ".join(map(str, chunk))
                    output_lines.append(line)
            else:
                # Should not happen in graph state usually
                # Just write it as is
                args_str = "(" + ",".join(map(str, args)) + ")" if args else ""
                t_str = " ".join(map(str, t_vals))
                output_lines.append(f"{name}{args_str} {t_str}")

    with open("candidate_clean.stim", "w") as f:
        f.write("\n".join(output_lines))

    print("Candidate generated in candidate_clean.stim")

if __name__ == "__main__":
    main()
