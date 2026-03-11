import stim
import sys

def solve():
    # Read stabilizers
    with open('target_stabilizers_anpaz.txt', 'r') as f:
        lines = [l.strip() for l in f if l.strip()]
    
    stabilizers = []
    for line in lines:
        stabilizers.append(stim.PauliString(line))

    # Create tableau
    t = stim.Tableau.from_stabilizers(stabilizers, allow_underconstrained=True)

    # Synthesize circuit
    # method='graph_state'
    circuit = t.to_circuit(method="graph_state")
    
    # Post-process circuit
    new_circuit = stim.Circuit()
    
    def append_chunked(name, targets):
        chunk_size = 10
        # For 2-qubit gates, chunk_size must be even
        if name in ["CX", "CY", "CZ", "CPHASE", "SWAP", "ISWAP"]:
            chunk_size = 10 # 5 pairs
        
        for i in range(0, len(targets), chunk_size):
            chunk = targets[i:i+chunk_size]
            new_circuit.append(name, chunk)

    for instruction in circuit:
        if instruction.name == "CZ":
            targets = instruction.targets_copy()
            for i in range(0, len(targets), 2):
                c = targets[i].value
                t_idx = targets[i+1].value
                # CZ(c, t) = H(t) CX(c, t) H(t)
                new_circuit.append("H", [t_idx])
                new_circuit.append("CX", [c, t_idx])
                new_circuit.append("H", [t_idx])
        elif instruction.name == "RX":
            # RX assumes reset to 0 then H.
            # We assume start at 0. So just H.
            targets = instruction.targets_copy()
            append_chunked("H", [t.value for t in targets])
        elif instruction.name == "R":
            # Reset to 0. We assume start at 0. Ignore.
            pass
        elif instruction.name in ["H", "S", "X", "Y", "Z"]:
             append_chunked(instruction.name, [t.value for t in instruction.targets_copy()])
        elif instruction.name == "CX":
             append_chunked("CX", [t.value for t in instruction.targets_copy()])
        else:
            # Other gates? Just append as is, or handle if needed.
            # For this task, mostly Clifford gates.
            new_circuit.append(instruction)

    # Write to file
    with open('candidate.stim', 'w') as f:
        f.write(str(new_circuit))
    print("Candidate written to candidate.stim")

if __name__ == "__main__":
    solve()
