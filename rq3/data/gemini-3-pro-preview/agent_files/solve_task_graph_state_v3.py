import stim
import sys

def solve():
    # Load stabilizers
    with open('target_stabilizers_job.txt', 'r') as f:
        stabilizers = [line.strip().replace(',', '') for line in f if line.strip()]
    
    # Check if stabilizers are empty
    if not stabilizers:
        print("No stabilizers found.")
        return

    num_qubits = len(stabilizers[0])
    
    # Method 1: Try from stabilizers directly
    try:
        tableau = stim.Tableau.from_stabilizers(stabilizers)
        circuit = tableau.to_circuit(method='graph_state')
        
        # Post-process: Replace RX with H for |0> input
        # graph_state synthesis often outputs RX gates to prepare |+> from |0>.
        # But if we start with |0>, RX is a reset. We want unitary.
        # RX(k) is equivalent to H(k) if input is |0> (creates |+>).
        # We need to be careful. Stim's graph_state output usually looks like:
        # RX 0 1 2 ...
        # CZ ...
        # ...
        # If the circuit starts with RX, we can replace with H.
        
        new_circuit = stim.Circuit()
        for instr in circuit:
            if instr.name == 'RX':
                # Replace RX with H
                new_circuit.append('H', instr.targets_copy())
            else:
                new_circuit.append(instr)
        
        with open('candidate_graph.stim', 'w') as f:
            f.write(str(new_circuit))
        print("Generated candidate_graph.stim from stabilizers")
        return

    except Exception as e:
        print(f"Failed to synthesize from stabilizers directly: {e}")

    # Method 2: Try from baseline tableau
    try:
        with open('baseline_task.stim', 'r') as f:
            baseline = stim.Circuit(f.read())
        
        sim = stim.TableauSimulator()
        sim.do(baseline)
        # The stabilizers of the state are effectively what the circuit prepares (from |0>).
        # We want a circuit that prepares the SAME state.
        # So we can extract the tableau of the current state.
        # Note: current_inverse_tableau() gives the operation that undoes the circuit.
        # So inverse() of that is the circuit's operation (clifford).
        # But we want the STATE stabilizers.
        # Actually, `Tableau.from_stabilizers` expects a list of Pauli strings.
        # If we just want a circuit that prepares the same state as baseline:
        current_tableau = sim.current_inverse_tableau().inverse()
        
        # Synthesize from this tableau
        # We can use method='graph_state' on the tableau directly.
        circuit = current_tableau.to_circuit(method='graph_state')
        
        new_circuit = stim.Circuit()
        for instr in circuit:
            if instr.name == 'RX':
                new_circuit.append('H', instr.targets_copy())
            else:
                new_circuit.append(instr)
                
        with open('candidate_graph.stim', 'w') as f:
            f.write(str(new_circuit))
        print("Generated candidate_graph.stim from baseline tableau")

    except Exception as e:
        print(f"Failed to synthesize from baseline: {e}")

if __name__ == "__main__":
    solve()
