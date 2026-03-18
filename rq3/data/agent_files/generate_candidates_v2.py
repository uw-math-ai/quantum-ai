import stim
import sys

def count_cx(circuit):
    count = 0
    for instr in circuit:
        if instr.name in ["CX", "CNOT"]:
            count += len(instr.targets_copy()) // 2
    return count

def main():
    with open("baseline.stim", "r") as f:
        baseline_text = f.read()
    
    baseline = stim.Circuit(baseline_text)
    print(f"Baseline CX count: {count_cx(baseline)}")
    
    # Simulate to get tableau
    sim = stim.TableauSimulator()
    sim.do(baseline)
    tableau = sim.current_inverse_tableau().inverse()
    
    # Method 1: graph_state
    candidate1 = tableau.to_circuit(method="graph_state")
    
    # Clean candidate1
    final_cand1 = stim.Circuit()
    for instr in candidate1:
        if instr.name == "RX":
            final_cand1.append("H", instr.targets_copy())
        elif instr.name == "TICK":
            continue
        else:
            final_cand1.append(instr)
            
    print(f"Candidate 1 (graph_state) CX count: {count_cx(final_cand1)}")
    
    with open("candidate1.stim", "w") as f:
        f.write(str(final_cand1))
        
    # Method 2: elimination
    candidate2 = tableau.to_circuit(method="elimination")
    
    # Clean candidate2
    final_cand2 = stim.Circuit()
    for instr in candidate2:
        if instr.name == "RX":
            final_cand2.append("H", instr.targets_copy())
        elif instr.name == "TICK":
            continue
        else:
            final_cand2.append(instr)
            
    print(f"Candidate 2 (elimination) CX count: {count_cx(final_cand2)}")
    
    with open("candidate2.stim", "w") as f:
        f.write(str(final_cand2))

if __name__ == "__main__":
    main()
