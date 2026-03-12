
import stim
import sys

def solve():
    # Load baseline
    try:
        with open(r'current_task_baseline.stim', 'r') as f:
            baseline_text = f.read()
        baseline = stim.Circuit(baseline_text)
    except Exception as e:
        print(f"Error loading baseline: {e}", file=sys.stderr)
        return

    # Simulate to get tableau
    sim = stim.TableauSimulator()
    sim.do(baseline)
    tableau = sim.current_inverse_tableau().inverse()
    
    # Synthesize
    circuit = tableau.to_circuit(method="graph_state")
    
    # Post-process
    new_circuit = stim.Circuit()
    for instruction in circuit:
        if instruction.name == "RX":
            for target in instruction.targets_copy():
                new_circuit.append("H", [target])
        elif instruction.name == "R":
            pass
        elif instruction.name in ["M", "MX", "MY", "MZ"]:
             # Keep measurements if any (unlikely for state prep)
             new_circuit.append(instruction)
        else:
            new_circuit.append(instruction)
            
    print(new_circuit)

if __name__ == "__main__":
    solve()
