import stim

stabilizers = [
    "XXIIIIXXIIIIXXIIIIXXIIIIXXIIIIXXIIII",
    "XIXIIIXIXIIIXIXIIIXIXIIIXIXIIIXIXIII",
    "XIIXIIXIIXIIXIIXIIXIIXIIXIIXIIXIIXII",
    "XIIIXIXIIIXIXIIIXIXIIIXIXIIIXIXIIIXI",
    "XXXXXXIIIIIIIIIIIIIIIIIIIIIIIIIIIIII",
    "IIIIIIXXXXXXIIIIIIIIIIIIIIIIIIIIIIII",
    "IIIIIIIIIIIIXXXXXXIIIIIIIIIIIIIIIIII",
    "IIIIIIIIIIIIIIIIIIXXXXXXIIIIIIIIIIII",
    "IIIIIIIIIIIIIIIIIIIIIIIIXXXXXXIIIIII",
    "IIIIIIIIIIIIIIIIIIIIIIIIIIIIIIXXXXXX",
    "ZZIIIIZZIIIIZZIIIIZZIIIIZZIIIIZZIIII",
    "ZIZIIIZIZIIIZIZIIIZIZIIIZIZIIIZIZIII",
    "ZIIZIIZIIZIIZIIZIIZIIZIIZIIZIIZIIZII",
    "ZIIIZIZIIIZIZIIIZIZIIIZIZIIIZIZIIIZI",
    "ZZZZZZIIIIIIIIIIIIIIIIIIIIIIIIIIIIII",
    "IIIIIIZZZZZZIIIIIIIIIIIIIIIIIIIIIIII",
    "IIIIIIIIIIIIZZZZZZIIIIIIIIIIIIIIIIII",
    "IIIIIIIIIIIIIIIIIIZZZZZZIIIIIIIIIIII",
    "IIIIIIIIIIIIIIIIIIIIIIIIZZZZZZIIIIII",
    "IIIIIIIIIIIIIIIIIIIIIIIIIIIIIIZZZZZZ"
]

def solve():
    # Parse stabilizers into a Tableau
    # Since we have fewer stabilizers than qubits (20 vs 36), the state is not unique.
    # We need to find *a* state that satisfies these.
    # stim.Tableau.from_stabilizers can handle this if we allow underconstrained.
    
    try:
        t = stim.Tableau.from_stabilizers(
            [stim.PauliString(s) for s in stabilizers],
            allow_redundant=True,
            allow_underconstrained=True
        )
        
        # Synthesize a circuit that prepares this tableau
        circuit = t.to_circuit("elimination")
        # Print the circuit to a file to ensure clean output
        with open("circuit_36.stim", "w") as f:
            print(circuit, file=f)
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    solve()
