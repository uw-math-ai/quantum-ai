import stim
import os

def solve():
    try:
        with open("current_baseline.stim", "r") as f:
            baseline_text = f.read()
    except FileNotFoundError:
        print("Error: current_baseline.stim not found")
        return

    try:
        baseline = stim.Circuit(baseline_text)
    except Exception as e:
        print(f"Error parsing baseline: {e}")
        return

    sim = stim.TableauSimulator()
    sim.do(baseline)
    # Get the tableau that maps Z basis (at input) to the current state (at output).
    # current_inverse_tableau() gives T^-1 where T|0> = |psi>.
    # So we want T = sim.current_inverse_tableau().inverse().
    current_tableau = sim.current_inverse_tableau().inverse()

    # Synthesize using graph state
    candidate = current_tableau.to_circuit(method="graph_state")

    final_circuit = stim.Circuit()
    for instruction in candidate:
        if instruction.name == "RX":
            # Replace RX (reset X) with H (Hadamard on |0>)
            # Since we assume start state is |0>, H|0> = |+>. RX prepares |+>.
            final_circuit.append("H", instruction.targets_copy())
        elif instruction.name == "TICK":
            continue
        else:
            final_circuit.append(instruction)

    with open("attempt_1.stim", "w") as f:
        f.write(str(final_circuit))
    print("Wrote attempt_1.stim")

if __name__ == "__main__":
    solve()
