import stim

def generate_optimized():
    try:
        with open("baseline_rq3.stim", "r") as f:
            baseline_text = f.read()
        
        baseline = stim.Circuit(baseline_text)
        
        # Simulate to get the tableau
        sim = stim.TableauSimulator()
        sim.do(baseline)
        tableau = sim.current_inverse_tableau().inverse()
        
        # Synthesize using graph_state
        optimized = tableau.to_circuit(method="graph_state")
        
        # Post-process to replace RX with H and remove TICK
        final_circuit = stim.Circuit()
        for instruction in optimized:
            if instruction.name == "RX":
                # RX resets to |+>. From |0>, H does the same.
                final_circuit.append("H", instruction.targets_copy())
            elif instruction.name == "TICK":
                continue
            else:
                final_circuit.append(instruction)
        
        print(final_circuit)
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    generate_optimized()