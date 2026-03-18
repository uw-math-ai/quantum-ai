import stim
import sys

def main():
    try:
        with open('baseline_rq3.stim', 'r') as f:
            baseline_text = f.read()
        baseline = stim.Circuit(baseline_text)
        
        sim = stim.TableauSimulator()
        sim.do(baseline)
        
        # We need the inverse tableau to reconstruct the circuit
        # The tableau maps X_in to X_out, Z_in to Z_out.
        # We want a circuit that performs this mapping.
        # stim.Tableau.to_circuit() does this.
        # However, to_circuit(method='graph_state') produces a state preparation circuit 
        # that prepares the output state from |0> (or |+>).
        # It assumes the input is unimportant (resets used) OR it is a unitary?
        # Actually, 	o_circuit(method='graph_state') produces a circuit that PREPARES the stabilizer state
        # defined by the tableau's Z outputs (stabilizers) and X outputs (destabilizers).
        # It usually starts with resets.
        # Since we want to optimize the baseline which starts from |0>, this is perfect.
        # We just need to replace the resets with H if we assume input is |0>.
        
        # Get the current state as a tableau
        # Note: stim's simulator tracks the frame. 
        # To get a circuit that prepares the SAME state from |0>, we just need the stabilizers.
        # But to be safe and match exactly, we use the full tableau.
        
        current_tableau = sim.current_inverse_tableau().inverse()
        
        # Generate the graph state circuit
        # method='graph_state' is optimized for 2-qubit gate count (using CZ).
        candidate = current_tableau.to_circuit(method='graph_state')
        
        # Clean up the circuit: Replace RX with H (assuming input |0>)
        clean_circuit = stim.Circuit()
        for instr in candidate:
            if instr.name == 'RX':
                # RX resets to |+> (Reset Z then H, or Reset X).
                # In Stim, RX is "Reset to X basis". It leaves the qubit in |+>.
                # If we start from |0>, H leaves the qubit in |+>.
                # So RX on |0> is equivalent to H on |0>.
                clean_circuit.append('H', instr.targets_copy())
            elif instr.name == 'MY': # Measurement Y - shouldn't happen
                clean_circuit.append(instr)
            elif instr.name == 'MZ': # Measurement Z - shouldn't happen
                clean_circuit.append(instr) 
            else:
                clean_circuit.append(instr)
        
        # Output the clean circuit
        print(clean_circuit)
        
    except Exception as e:
        print(f'Error: {e}', file=sys.stderr)

if __name__ == '__main__':
    main()
