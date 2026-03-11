import stim
import sys

def optimize_circuit_elimination():
    # Load the baseline circuit
    with open("current_baseline.stim", "r") as f:
        baseline_str = f.read()
    baseline = stim.Circuit(baseline_str)

    sim = stim.TableauSimulator()
    sim.do(baseline)
    tableau = sim.current_inverse_tableau().inverse()
    
    print("Synthesizing using elimination method...")
    re_synthesized = tableau.to_circuit(method="elimination")
    
    return re_synthesized

if __name__ == "__main__":
    circuit = optimize_circuit_elimination()
    print(circuit)
