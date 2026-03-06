import stim

def main():
    try:
        # Load baseline
        with open("baseline.stim", "r") as f:
            baseline_text = f.read()
        baseline = stim.Circuit(baseline_text)
        
        print(f"Baseline qubits: {baseline.num_qubits}")
        
        # Get tableau from baseline
        sim = stim.TableauSimulator()
        sim.do(baseline)
        tableau = sim.current_inverse_tableau() ** -1 # Get the forward tableau
        
        # Or just:
        tableau = stim.Tableau.from_circuit(baseline)
        
        # Synthesize
        synthesized = tableau.to_circuit("graph_state")
        
        # Clean
        clean_circuit = stim.Circuit()
        for instr in synthesized:
            if instr.name == "RX":
                clean_circuit.append("H", instr.targets_copy())
            elif instr.name == "TICK":
                continue
            elif instr.name == "CZ":
                targets = instr.targets_copy()
                for i in range(0, len(targets), 2):
                    c = targets[i]
                    t = targets[i+1]
                    clean_circuit.append("H", [t])
                    clean_circuit.append("CX", [c, t])
                    clean_circuit.append("H", [t])
            else:
                clean_circuit.append(instr)
                
        # Metrics
        cx = 0
        for instr in clean_circuit:
            if instr.name in ["CX", "CNOT"]:
                cx += len(instr.targets_copy()) // 2
        
        print(f"Resynthesized CX: {cx}")
        
        with open("candidate_resynth.stim", "w") as f:
            f.write(str(clean_circuit))
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
