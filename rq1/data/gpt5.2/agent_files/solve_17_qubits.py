import stim
import sys

def solve():
    # Stabilizers from the prompt
    stabilizers = [
        "IIIIIXIIIXIXXIIII",
        "IIIIIIIIXIXIIXIXI",
        "IIIXIIIXIIIIIIXIX",
        "IIXIIIXIIIIIIIXIX",
        "IIIIXXXXXIXXIIIIX",
        "IXIIXIIIIIXIIXIII",
        "IIIIIIIIXXIXIIIXI",
        "XIXXIIIIIIIIIIXII",
        "IIIIIZIIIZIZZIIII",
        "IIIIIIIIZIZIIZIZI",
        "IIIZIIIZIIIIIIZIZ",
        "IIZIIIZIIIIIIIZIZ",
        "IIIIZZZZZIZZIIIIZ",
        "IZIIZIIIIIZIIZIII",
        "IIIIIIIIZZIZIIIZI",
        "ZIZZIIIIIIIIIIZII"
    ]

    # Convert to Stim format
    # stim.Tableau.from_stabilizers requires a list of stim.PauliString
    pauli_strings = [stim.PauliString(s) for s in stabilizers]

    try:
        # Attempt to find a state that satisfies these stabilizers
        # allow_underconstrained=True is important if the stabilizers don't fully specify the state (less than N generators for N qubits)
        # Here we have 16 generators for 17 qubits? Wait, let's count.
        # 8 X generators + 8 Z generators = 16 generators.
        # If qubits = 17, then it is underconstrained (1 logical qubit).
        
        tableau = stim.Tableau.from_stabilizers(pauli_strings, allow_underconstrained=True)
        
        # Generate the circuit that prepares this tableau from |0...0>
        # 'elimination' method usually works well for stabilizer states
        circuit = tableau.to_circuit(method="elimination")
        
        print(circuit)
        
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)

if __name__ == "__main__":
    solve()
