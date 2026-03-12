import stim

def main():
    try:
        # Load baseline circuit
        with open("baseline_job.stim", "r") as f:
            baseline = stim.Circuit(f.read())
            
        # Simulate to get the tableau
        sim = stim.TableauSimulator()
        sim.do(baseline)
        tableau = sim.current_inverse_tableau().inverse()
        
        # Synthesize circuit using graph_state method
        circuit = tableau.to_circuit(method="graph_state")

        # Replace RX with H
        new_circuit = stim.Circuit()
        for instruction in circuit:
            if instruction.name == "RX":
                targets = instruction.targets_copy()
                new_circuit.append("H", targets)
            else:
                new_circuit.append(instruction)

        with open("candidate_from_baseline.stim", "w") as f:
            print(new_circuit, file=f)
            
        print("Candidate generated successfully.")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
