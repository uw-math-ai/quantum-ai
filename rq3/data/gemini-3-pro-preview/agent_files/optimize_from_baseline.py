import stim

def clean_circuit(circ):
    new_circ = stim.Circuit()
    for instruction in circ:
        if instruction.name == "R":
            continue # Assume start at |0>
        elif instruction.name == "RX":
            # RX resets to |+>. If we start at |0>, H does that.
            for t in instruction.targets_copy():
                new_circ.append("H", [t])
        elif instruction.name in ["M", "MX", "MY", "MZ"]:
             continue # No measurements
        else:
            new_circ.append(instruction)
    return new_circ

def main():
    try:
        with open("baseline.stim", "r") as f:
            baseline_text = f.read()
        
        circuit = stim.Circuit(baseline_text)
        sim = stim.TableauSimulator()
        sim.do(circuit)
        tableau = sim.current_inverse_tableau() ** -1
        
        # Method 1: Graph State
        circ_graph = tableau.to_circuit(method="graph_state")
        cleaned_graph = clean_circuit(circ_graph)
        
        with open("candidate_graph.stim", "w") as f:
            f.write(str(cleaned_graph))
        
        # Method 2: Elimination (standard)
        circ_elim = tableau.to_circuit(method="elimination")
        cleaned_elim = clean_circuit(circ_elim)
        
        with open("candidate_elim.stim", "w") as f:
            f.write(str(cleaned_elim))

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
