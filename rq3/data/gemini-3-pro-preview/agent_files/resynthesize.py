import stim
import sys

def main():
    try:
        # 1. Read baseline circuit
        with open(r"C:\Users\anpaz\Repos\quantum-ai\rq3\data\gemini-3-pro-preview\agent_files\baseline_correct.stim", "r") as f:
            baseline_text = f.read()
        
        baseline_circuit = stim.Circuit(baseline_text)
        
        # 2. Get Tableau from circuit
        # We assume the circuit acts on |0...0>
        # The tableau represents the unitary U. 
        # U |0> is the state.
        # But to_circuit generates a circuit for the Tableau.
        # If the Tableau represents the stabilizer state, we are good.
        # stim.Tableau.from_circuit calculates the Heisenberg picture evolution.
        # It represents U.
        # If we want the state U|0>, we need the stabilizers of U|0>.
        # Actually, tableau.to_circuit() produces a circuit that implements the unitary of the tableau.
        # So it should be equivalent to the baseline circuit (up to phases/Clifford equivalency).
        
        tableau = stim.Tableau.from_circuit(baseline_circuit)
        
        # 3. Synthesize (Graph State)
        # This will produce a circuit optimized for CZ count (0 CX).
        try:
            new_circuit = tableau.to_circuit(method="graph_state")
        except Exception as e:
            print(f"Error synthesizing: {e}", file=sys.stderr)
            return

        # 4. Clean up RX gates
        # Graph state synthesis for a unitary might produce resets if it thinks we are starting from scratch 
        # but the tableau represents a transformation.
        # Wait, if we use from_circuit, we get a Tableau representing the UNITARY.
        # If the baseline is just a state prep (starting from |0>), then the unitary applied to |0> is the state.
        # However, to_circuit(method="graph_state") creates a circuit that implements the *Tableau*.
        # If the Tableau has X outputs for Z inputs (due to H gates), it handles it.
        # The issue is `RX`. 
        # If the circuit assumes input is arbitrary, it can't use `RX` unless it's a reset.
        # But if we know input is |0>, we can replace `RX` with `H` (if it was `RX` on input).
        # Actually, `method="graph_state"` usually produces a circuit that prepares a graph state *from |+>*.
        # So it starts with H on all qubits, then CZs, then local Cliffords.
        # It does NOT use RX unless it needs to reset an ancilla.
        # Let's see what it produces.
        
        circuit_str = str(new_circuit)
        
        new_lines = []
        for line in circuit_str.splitlines():
            stripped = line.strip()
            if stripped.startswith("RX"):
                # Use H if we assume |0> input.
                # But wait, if the baseline has 68 qubits, and the tableau is 68 qubits.
                targets = stripped[2:].strip()
                new_lines.append(f"H {targets}")
            elif stripped.startswith("M"):
                 pass
            else:
                new_lines.append(line)
        
        final_circuit_str = "\n".join(new_lines)
        print(final_circuit_str)

    except Exception as e:
        print(f"Failed: {e}", file=sys.stderr)

if __name__ == "__main__":
    main()
