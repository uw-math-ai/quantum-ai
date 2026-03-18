import stim
import re

def load_stabilizers(path):
    with open(path, 'r') as f:
        lines = [line.strip() for line in f if line.strip()]
    cleaned = []
    for line in lines:
        if ". " in line:
            line = line.split(". ", 1)[1]
        cleaned.append(line)
    return cleaned

def get_metrics(circuit):
    cx = 0
    vol = 0
    for instr in circuit:
        n_targets = len(instr.targets_copy())
        if instr.name == "CX":
            n = n_targets // 2
            cx += n
            vol += n
        elif instr.name in ["CY", "CZ", "SWAP", "ISWAP", "ISWAP_DAG"]:
            n = n_targets // 2
            vol += n
        else:
            vol += n_targets
    return cx, vol

def convert_rx_to_h(circuit):
    new_circuit = stim.Circuit()
    for instr in circuit:
        if instr.name == "RX":
            # RX targets are qubits to reset to X.
            # Equivalent to H on |0>.
            # If targets are 0, 1, 2...
            # Add H 0 1 2...
            new_circuit.append("H", instr.targets_copy())
        elif instr.name == "R":
            # Reset to Z. Equivalent to I on |0>.
            # Do nothing? Or ensure |0>?
            # If input is |0>, R is identity.
            pass
        elif instr.name == "RZ":
             # Same as R?
             pass
        else:
            new_circuit.append(instr)
    return new_circuit

def solve():
    print("Testing graph state synthesis...")
    
    # Load stabilizers
    stabs = [stim.PauliString(s) for s in load_stabilizers("data/agent_files/target_stabilizers.txt")]
    
    try:
        tableau = stim.Tableau.from_stabilizers(stabs, allow_underconstrained=True)
        # Synthesize with graph_state
        # This produces RX, CZ, ...
        circuit_g = tableau.to_circuit("graph_state")
        
        # Convert RX to H
        circuit_fixed = convert_rx_to_h(circuit_g)
        
        # Check metrics
        cx, vol = get_metrics(circuit_fixed)
        print(f"Graph State: CX={cx}, Vol={vol}")
        
        # Check validity
        sim = stim.TableauSimulator()
        sim.do(circuit_fixed)
        valid = True
        for p in stabs:
            if sim.peek_observable_expectation(p) != 1:
                valid = False
                break
        
        if valid:
            print("Graph State is VALID.")
            with open("data/agent_files/candidate_graph_state.stim", "w") as f:
                f.write(str(circuit_fixed))
        else:
            print("Graph State is INVALID.")
            
    except Exception as e:
        print(f"Failed: {e}")

if __name__ == "__main__":
    solve()
