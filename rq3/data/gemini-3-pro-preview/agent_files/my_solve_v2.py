import stim
import sys

# Target stabilizers from the prompt
stabilizers = [
    "XZZXIIIIIIIIIIIIIIIIIIIIIIIIIIIIIII",
    "IIIIIXZZXIIIIIIIIIIIIIIIIIIIIIIIIII",
    "IIIIIIIIIIXZZXIIIIIIIIIIIIIIIIIIIII",
    "IIIIIIIIIIIIIIIXZZXIIIIIIIIIIIIIIII",
    "IIIIIIIIIIIIIIIIIIIIXZZXIIIIIIIIIII",
    "IIIIIIIIIIIIIIIIIIIIIIIIIXZZXIIIIII",
    "IIIIIIIIIIIIIIIIIIIIIIIIIIIIIIXZZXI",
    "IXZZXIIIIIIIIIIIIIIIIIIIIIIIIIIIIII",
    "IIIIIIXZZXIIIIIIIIIIIIIIIIIIIIIIIII",
    "IIIIIIIIIIIXZZXIIIIIIIIIIIIIIIIIIII",
    "IIIIIIIIIIIIIIIIXZZXIIIIIIIIIIIIIII",
    "IIIIIIIIIIIIIIIIIIIIXZZXIIIIIIIIII",
    "IIIIIIIIIIIIIIIIIIIIIIIIIIXZZXIIIII",
    "IIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIXZZX",
    "XIXZZIIIIIIIIIIIIIIIIIIIIIIIIIIIIII",
    "IIIIIXIXZZIIIIIIIIIIIIIIIIIIIIIIIII",
    "IIIIIIIIIIXIXZZIIIIIIIIIIIIIIIIIIII",
    "IIIIIIIIIIIIIIIXIXZZIIIIIIIIIIIIIII",
    "IIIIIIIIIIIIIIIIIIIIXIXZZIIIIIIIIII",
    "IIIIIIIIIIIIIIIIIIIIIIIIIXIXZZIIIII",
    "IIIIIIIIIIIIIIIIIIIIIIIIIIIIIIXIXZZ",
    "ZXIXZIIIIIIIIIIIIIIIIIIIIIIIIIIIIII",
    "IIIIIZXIXZIIIIIIIIIIIIIIIIIIIIIIIII",
    "IIIIIIIIIIZXIXZIIIIIIIIIIIIIIIIIIII",
    "IIIIIIIIIIIIIIIZXIXZIIIIIIIIIIIIIII",
    "IIIIIIIIIIIIIIIIIIIIZXIXZIIIIIIIIII",
    "IIIIIIIIIIIIIIIIIIIIIIIIIZXIXZIIIII",
    "IIIIIIIIIIIIIIIIIIIIIIIIIIIIIIZXIXZ",
    "IIIIIIIIIIXXXXXIIIIIXXXXXXXXXXXXXXX",
    "IIIIIXXXXXIIIIIXXXXXIIIIIXXXXXXXXXX",
    "XXXXXXXXXXXXXXXIIIIIIIIIIXXXXXIIIII",
    "IIIIIIIIIIZZZZZIIIIIZZZZZZZZZZZZZZZ",
    "IIIIIZZZZZIIIIIZZZZZIIIIIZZZZZZZZZZ",
    "ZZZZZZZZZZZZZZZIIIIIIIIIIZZZZZIIIII"
]

def synthesize():
    try:
        # Convert to PauliString objects
        pauli_stabs = [stim.PauliString(s) for s in stabilizers]
        
        # Create tableau
        # Using allow_underconstrained=True because 34 stabs for 35 qubits
        tableau = stim.Tableau.from_stabilizers(pauli_stabs, allow_redundant=True, allow_underconstrained=True)
        
        # Synthesize using graph_state method
        circuit = tableau.to_circuit(method="graph_state")
        
        # Post-process: Replace RX with H, Remove R/M
        new_circuit = stim.Circuit()
        for instr in circuit:
            if instr.name == "RX":
                # Replace RX with H
                new_circuit.append("H", instr.targets_copy())
            elif instr.name in ["R", "RZ", "M", "MX", "MY", "MZ"]:
                pass
            else:
                new_circuit.append(instr)
                
        print(new_circuit)

    except Exception as e:
        sys.stderr.write(f"Error: {e}\n")
        sys.exit(1)

if __name__ == "__main__":
    synthesize()
