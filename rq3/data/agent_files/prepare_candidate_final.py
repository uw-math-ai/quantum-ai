import stim
import sys

def prepare():
    try:
        with open("candidate_graph.stim", "r") as f:
            content = f.read()
            # Parse as stim circuit
            circuit = stim.Circuit(content)
            
        new_circuit = stim.Circuit()
        
        for instruction in circuit:
            if instruction.name == "RX":
                # Replace RX with H
                targets = instruction.targets_copy()
                new_circuit.append("H", targets)
            elif instruction.name == "TICK":
                new_circuit.append("TICK")
            else:
                new_circuit.append(instruction)
                
        # Save to candidate_submission.stim
        with open("candidate_submission.stim", "w") as f:
            f.write(str(new_circuit))
            
        print("Prepared candidate_submission.stim")
        
    except Exception as e:
        print(f"Error preparing submission: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    prepare()
