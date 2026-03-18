import stim

def main():
    # Load baseline
    with open("baseline_job_v8.stim", "r") as f:
        baseline_text = f.read()
    baseline = stim.Circuit(baseline_text)

    # Simulate to get tableau
    sim = stim.TableauSimulator()
    sim.do(baseline)
    tableau = sim.current_inverse_tableau().inverse()

    # Generate graph state circuit
    try:
        candidate = tableau.to_circuit(method="graph_state")
    except Exception as e:
        print(f"Error generating graph state: {e}")
        return

    # Post-process
    new_circuit = stim.Circuit()
    for instr in candidate:
        if instr.name == "RX":
            # Replace RX with H. RX resets to |+>. Input |0> -> H -> |+>.
            new_circuit.append(stim.CircuitInstruction("H", instr.targets_copy()))
        elif instr.name == "R":
            pass
        elif instr.name == "MY":
             new_circuit.append(instr)
        else:
            # Split large instructions to avoid line wrapping issues
            if len(instr.targets_copy()) > 10:
                targets = instr.targets_copy()
                # For 2-qubit gates like CZ, targets are pairs.
                # For 1-qubit gates like H, targets are singles.
                
                # Check gate arity
                # standard graph state gates: H (1), S (1), CZ (2), X/Y/Z (1)
                
                if instr.name in ["CZ", "CX", "CNOT", "CY", "SWAP"]:
                    # 2-qubit gates. Process in pairs.
                    for i in range(0, len(targets), 2):
                        new_circuit.append(stim.CircuitInstruction(instr.name, targets[i:i+2]))
                else:
                    # 1-qubit gates or others. Process singly (or in small batches)
                    # Let's just do singly for safety to avoid ANY wrapping
                    for t in targets:
                         new_circuit.append(stim.CircuitInstruction(instr.name, [t]))
            else:
                new_circuit.append(instr)
            
    # Output
    out_file = "candidate_job_v8_split.stim"
    with open(out_file, "w") as f:
        f.write(str(new_circuit).replace("CX", "CX")) # Ensure string format

    print(f"Written to {out_file}")

if __name__ == "__main__":
    main()
