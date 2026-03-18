import stim

def generate_graph_state_candidate():
    try:
        baseline = stim.Circuit.from_file("baseline_rq3_prompt.stim")
    except Exception as e:
        import os
        print(f"CWD: {os.getcwd()}")
        print(f"Error parsing baseline: {e}")
        return

    sim = stim.TableauSimulator()
    sim.do(baseline)
    tableau = sim.current_inverse_tableau().inverse()

    try:
        candidate = tableau.to_circuit(method="graph_state")
    except Exception as e:
        print(f"Error synthesizing: {e}")
        return

    # Post-process: Replace RX gates (resets) with H gates (Cliffords) 
    # assuming we are transforming |0> to the target stabilizer state.
    new_cand = stim.Circuit()
    for instruction in candidate:
        if instruction.name == "RX":
            for target in instruction.targets_copy():
                new_cand.append("H", [target])
        else:
            new_cand.append(instruction)
            
    print(new_cand)

if __name__ == "__main__":
    generate_graph_state_candidate()
