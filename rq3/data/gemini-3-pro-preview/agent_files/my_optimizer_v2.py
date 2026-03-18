import stim
import sys

def read_stabilizers(filename):
    with open(filename, 'r') as f:
        # Read the whole file content
        content = f.read()
    # The format in the prompt is a block of text with commas.
    # It might have newlines.
    # We want to split by comma.
    stabilizers = [s.strip() for s in content.replace('\n', '').split(',') if s.strip()]
    return stabilizers

def solve():
    stabilizers = read_stabilizers("target_stabilizers_prompt.txt")
    
    # Create PauliStrings
    try:
        paulis = [stim.PauliString(s) for s in stabilizers]
    except Exception as e:
        print(f"Error parsing stabilizers: {e}", file=sys.stderr)
        return

    # Synthesize
    try:
        # allow_redundant=True is crucial as stabilizers might be linearly dependent
        # allow_underconstrained=True allows the synthesizer to pick convenient values for unspecified degrees of freedom
        tableau = stim.Tableau.from_stabilizers(paulis, allow_redundant=True, allow_underconstrained=True)
        circuit = tableau.to_circuit(method="graph_state")
        
        # Post-process: Replace RX with H
        new_circuit = stim.Circuit()
        for instr in circuit:
            if instr.name == "RX":
                for target in instr.targets_copy():
                    new_circuit.append("H", [target])
            else:
                new_circuit.append(instr)
        
        with open("candidate.stim", "w") as f:
            print(new_circuit, file=f)
        print("Candidate written to candidate.stim")
        
    except Exception as e:
        print(f"Error during synthesis: {e}", file=sys.stderr)

if __name__ == "__main__":
    solve()
