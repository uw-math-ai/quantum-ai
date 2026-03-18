import stim

def optimize_circuit():
    try:
        # Load baseline circuit
        with open('current_baseline.stim', 'r') as f:
            baseline_text = f.read()
        
        # Parse circuit
        circuit = stim.Circuit(baseline_text)

        # Convert to tableau to capture the stabilizer state
        sim = stim.TableauSimulator()
        sim.do_circuit(circuit)
        # We need the stabilizers of the output state
        # But wait, stim.Tableau.from_circuit(circuit) gives the channel/unitary?
        # No, from_circuit gives the tableau of the operation.
        # If we apply it to |0>, we get the state.
        
        # However, to_circuit("graph_state") works on a Tableau representing a stabilizer state?
        # Or a Clifford operation?
        # "Returns a circuit that implements the tableau."
        # If the tableau represents a state (stabilizers of state), it prepares that state.
        # If it represents a unitary, it implements that unitary.
        
        # The baseline circuit prepares a state from |0>.
        # So the tableau of the circuit is the operation U such that U|0> = |psi>.
        # We want a new circuit V such that V|0> = |psi> (same stabilizers).
        
        # Let's just use from_circuit(circuit).
        tableau = stim.Tableau.from_circuit(circuit)
        
        # Generate new circuit
        # method="graph_state" tries to make a graph state preparation circuit.
        # It assumes input is |0> and output is the target state?
        # Or does it decompose the unitary?
        # Documentation says: "Returns a circuit that implements the tableau."
        # So it decomposes the unitary.
        
        # If the unitary maps Z basis to the target state, then it works.
        
        optimized_circuit = tableau.to_circuit(method="graph_state")
        
        # Post-process: Replace RX with H (assuming start state |0>)
        # and remove TICKs
        out_str = str(optimized_circuit)
        lines = out_str.splitlines()
        new_lines = []
        for line in lines:
            if line.startswith("RX"):
                # RX <qubits> -> H <qubits>
                new_lines.append(line.replace("RX", "H"))
            elif line.startswith("TICK"):
                continue
            else:
                new_lines.append(line)
        
        final_str = "\n".join(new_lines)
        
        # Save to candidate file
        with open('candidate.stim', 'w') as f:
            f.write(final_str)
            
        print("Candidate circuit saved to candidate.stim")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    optimize_circuit()
