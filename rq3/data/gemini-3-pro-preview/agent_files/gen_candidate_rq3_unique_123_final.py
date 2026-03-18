import stim
import sys

def solve():
    try:
        with open("baseline_rq3_unique_123.stim", "r") as f:
            baseline_text = f.read()
        baseline = stim.Circuit(baseline_text)
    except FileNotFoundError:
        print("Baseline file not found.", file=sys.stderr)
        return

    sim = stim.TableauSimulator()
    sim.do(baseline)
    tab = sim.current_inverse_tableau().inverse()

    # Synthesize using graph state
    candidate = tab.to_circuit(method="graph_state")
    
    # Post-process
    new_candidate = stim.Circuit()
    for instruction in candidate:
        if instruction.name == "RX":
            new_candidate.append("H", instruction.targets_copy())
        elif instruction.name in ["R", "RZ"]:
            pass 
        elif instruction.name == "RY":
             targets = instruction.targets_copy()
             # RY prepares |+i>. H|0> -> |+>. S|+> -> |+i>.
             new_candidate.append("H", targets)
             new_candidate.append("S", targets)
        else:
            new_candidate.append(instruction)
            
    print(new_candidate)

if __name__ == "__main__":
    solve()
