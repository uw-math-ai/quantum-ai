import stim
import sys

target_stabilizers = [
    "IIIIIXIIIXIXXIIII", "IIIIIIIIXIXIIXIXI", "IIIXIIIXIIIIIIXIX", "IIXIIIXIIIIIIIXIX",
    "IIIIXXXXXIXXIIIIX", "IXIIXIIIIIXIIXIII", "IIIIIIIIXXIXIIIXI", "XIXXIIIIIIIIIIXII",
    "IIIIIZIIIZIZZIIII", "IIIIIIIIZIZIIZIZI", "IIIZIIIZIIIIIIZIZ", "IIZIIIZIIIIIIIZIZ",
    "IIIIZZZZZIZZIIIIZ", "IZIIZIIIIIZIIZIII", "IIIIIIIIZZIZIIIZI", "ZIZZIIIIIIIIIIZII"
]

def main():
    stabilizers = [stim.PauliString(s) for s in target_stabilizers]
    
    try:
        t = stim.Tableau.from_stabilizers(stabilizers, allow_underconstrained=True, allow_redundant=True)
    except Exception as e:
        print(f"Error creating tableau: {e}")
        return

    # Method: Graph State
    circuit = t.to_circuit(method="graph_state")
    
    clean_circuit = stim.Circuit()
    for op in circuit:
        if op.name == "RX":
            clean_circuit.append("H", op.targets_copy())
        elif op.name == "RZ":
            pass
        elif op.name == "MX" or op.name == "MY" or op.name == "MZ":
            pass # Remove measurements
        elif op.name == "R": # R is alias for RZ
            pass
        else:
            clean_circuit.append(op)
            
    with open("candidate_graph_state.stim", "w") as f:
        print(clean_circuit, file=f)
    print("Written to candidate_graph_state.stim")

if __name__ == "__main__":
    main()
