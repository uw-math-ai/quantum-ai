import stim
import sys

def generate_circuit():
    # Load targets
    try:
        with open("my_targets_v2.txt", "r") as f:
            lines = [l.strip() for l in f if l.strip()]
    except Exception as e:
        sys.stderr.write(f"Error opening targets: {e}\n")
        return

    # Create tableau from stabilizers
    try:
        t = stim.Tableau.from_stabilizers(lines, allow_underconstrained=True)
    except Exception as e:
        sys.stderr.write(f"Error creating tableau: {e}\n")
        return

    # Synthesis
    try:
        circ = t.to_circuit(method="graph_state")
    except Exception as e:
        sys.stderr.write(f"Error synthesizing circuit: {e}\n")
        return

    # Post-process to remove resets and handle RX
    cleaned_circ = stim.Circuit()
    
    # Track which qubits have been initialized/reset
    # We assume start state is |0...0>
    
    for instruction in circ:
        if instruction.name == "RX":
            # Reset to |+>. 
            # If this is the first operation on the qubit, it means we want to prepare |+>.
            # From |0>, we apply H.
            for t in instruction.targets_copy():
                cleaned_circ.append("H", [t])
        elif instruction.name == "R" or instruction.name == "RZ":
            # Reset to |0>.
            # If this is the first operation, it's redundant (we start at |0>).
            # If it's in the middle, it's a reset (forbidden).
            # Graph state synthesis usually puts resets at the beginning.
            pass
        elif instruction.name in ["M", "MX", "MY", "MZ"]:
             sys.stderr.write("Error: Circuit contains measurements.\n")
             return
        else:
            cleaned_circ.append(instruction)
            
    print(cleaned_circ)

if __name__ == "__main__":
    generate_circuit()
