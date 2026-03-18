import stim
import sys

def main():
    try:
        with open("stabilizers_rq3.txt", "r") as f:
            lines = [line.strip() for line in f if line.strip()]

        stabilizers = []
        for line in lines:
            stabilizers.append(stim.PauliString(line))

        # Create tableau from stabilizers
        # using allow_redundant and allow_underconstrained to be safe
        tableau = stim.Tableau.from_stabilizers(stabilizers, allow_redundant=True, allow_underconstrained=True)
        
        # Synthesize using graph state method
        circuit = tableau.to_circuit(method="graph_state")
        
        # Post-process:
        # method="graph_state" typically outputs a unitary circuit that maps |0> to the state.
        # It might use gates like H, S, CZ, CX, X, Y, Z.
        # It might also use RX, RY, RZ if it thinks it's doing resets.
        # But usually from_stabilizers -> to_circuit produces a unitary (without resets) if possible.
        # If the tableau is not invertible (underconstrained), it might produce something else?
        # Actually to_circuit(method="graph_state") works on Tableau, which is always $2^n \times 2^n$ invertible Clifford.
        # When we use allow_underconstrained=True, from_stabilizers pads the tableau to be full rank.
        # So the result is a valid unitary.
        
        print(circuit)
        
    except Exception as e:
        sys.stderr.write(str(e))
        sys.exit(1)

if __name__ == "__main__":
    main()