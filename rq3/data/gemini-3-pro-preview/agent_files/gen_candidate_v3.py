import stim
import sys

def solve():
    with open(r"C:\Users\anpaz\Repos\quantum-ai\rq3\baseline_v3.stim", "r") as f:
        baseline_text = f.read()
    
    circuit = stim.Circuit(baseline_text)
    sim = stim.TableauSimulator()
    sim.do(circuit)
    tableau = sim.current_inverse_tableau().inverse()
    
    # Synthesize
    # method='graph_state' is usually best for cx_count (uses CZs)
    candidate = tableau.to_circuit(method='graph_state')
    
    new_circuit = stim.Circuit()
    for instruction in candidate:
        if instruction.name == "RX":
            # RX target is reset to |+>.
            # Equivalent to H if input is |0>.
            for t in instruction.targets_copy():
                new_circuit.append("H", [t])
        elif instruction.name == "CZ":
             new_circuit.append(instruction)
        else:
            new_circuit.append(instruction)
            
    print(new_circuit)

if __name__ == "__main__":
    solve()
