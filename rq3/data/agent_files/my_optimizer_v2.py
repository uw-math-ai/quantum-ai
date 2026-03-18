import stim
import sys

def solve():
    # Read stabilizers
    with open('my_target_stabilizers.txt', 'r') as f:
        try:
            stabilizers = [stim.PauliString(line.strip()) for line in f if line.strip()]
        except Exception as e:
            print(f"Error parsing stabilizers: {e}")
            return

    # Create Tableau from stabilizers
    try:
        # Check if the baseline stabilizers are consistent
        # We can construct the tableau from stabilizers
        tableau = stim.Tableau.from_stabilizers(stabilizers, allow_underconstrained=True)
    except Exception as e:
        print(f"Error creating tableau: {e}")
        return

    # Try graph state synthesis (produces CZ gates -> CX count 0)
    # This is the most likely way to get 0 CX gates.
    try:
        circuit = tableau.to_circuit(method="graph_state")
        
        # Clean up RX/RY/RZ gates assuming start state |0>
        cleaned_circuit = stim.Circuit()
        for instr in circuit:
            if instr.name == "RX":
                # RX resets to |+>. From |0>, H does that.
                for target in instr.targets_copy():
                    cleaned_circuit.append("H", [target])
            elif instr.name == "RY":
                # RY resets to |i+>. From |0>, H then S does that.
                # |0> -H-> |+> -S-> |i+>
                for target in instr.targets_copy():
                    cleaned_circuit.append("H", [target])
                    cleaned_circuit.append("S", [target])
            elif instr.name == "RZ":
                # RZ resets to |0>. From |0>, do nothing.
                pass
            else:
                cleaned_circuit.append(instr)
        
        with open('candidate.stim', 'w') as f:
            print(cleaned_circuit, file=f)
            
        print("Candidate generated.")

    except Exception as e:
        print(f"Error synthesizing circuit: {e}")

if __name__ == "__main__":
    solve()
