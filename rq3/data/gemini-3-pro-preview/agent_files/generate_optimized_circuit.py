import stim

def main():
    try:
        # Load baseline
        with open("baseline.stim", "r") as f:
            baseline_str = f.read()
        
        circuit = stim.Circuit(baseline_str)
        num_qubits = circuit.num_qubits
        print(f"Baseline qubits: {num_qubits}")
        
        # Simulate to get tableau
        sim = stim.TableauSimulator()
        sim.do(circuit)
        tableau = sim.current_inverse_tableau().inverse()
        
        # Synthesize graph state
        # method='graph_state' ensures 0 CX count (uses CZ)
        raw_graph_circuit = tableau.to_circuit(method="graph_state")
        
        final_circuit = stim.Circuit()
        for instr in raw_graph_circuit:
            if instr.name == "RX":
                # RX is reset to |+>. H transforms |0> to |+>.
                targets = [t.value for t in instr.targets_copy() if t.value < num_qubits]
                if targets:
                    final_circuit.append("H", targets)
            elif instr.name == "TICK":
                final_circuit.append("TICK")
            elif instr.name == "CZ":
                # Filter pairs
                args = instr.gate_args_copy()
                targets = []
                raw_targets = instr.targets_copy()
                for i in range(0, len(raw_targets), 2):
                    t1 = raw_targets[i].value
                    t2 = raw_targets[i+1].value
                    if t1 < num_qubits and t2 < num_qubits:
                        targets.append(t1)
                        targets.append(t2)
                if targets:
                    final_circuit.append("CZ", targets, args)
            else:
                # Single qubit gates
                targets = [t.value for t in instr.targets_copy() if t.is_qubit_target and t.value < num_qubits]
                if targets:
                    final_circuit.append(instr.name, targets, instr.gate_args_copy())

        # Save to file
        with open("candidate.stim", "w") as f:
            f.write(str(final_circuit))
            
        print(f"Generated candidate with {len(final_circuit)} instructions.")
        print(f"Candidate saved to candidate.stim")

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
