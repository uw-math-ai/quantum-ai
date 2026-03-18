import stim

def solve():
    print("Loading baseline...")
    with open("baseline.stim", "r") as f:
        baseline_text = f.read()
    
    circuit = stim.Circuit(baseline_text)
    
    print("Simulating tableau...")
    sim = stim.TableauSimulator()
    sim.do(circuit)
    tableau = sim.current_inverse_tableau().inverse()
    
    print("Synthesizing graph state...")
    # method='graph_state' usually produces 0 CX gates (only CZs and single qubit gates)
    candidate = tableau.to_circuit(method="graph_state")
    
    print("Checking for RX gates...")
    # graph_state method might use RX gates which are resets? No, RX is rotation.
    # But usually it produces H, S, CZ, SQRT_X etc.
    # Wait, 'graph_state' synthesis might produce 'RX' if the tableau involves X basis.
    # However, standard stim circuits don't use 'RX' as a gate unless it's a reset?
    # Stim's 'RX' is a reset gate! R_X is rotation. 
    # 'graph_state' output uses H, S, CZ, etc.
    # Let's verify if there are any resets (R, RX, RY, RZ) or just gates.
    # If the output contains resets, we might need to replace them with gates if the input is |0>.
    # But sim.current_inverse_tableau().inverse() represents the unitary evolution from |0> if the circuit had no resets.
    # If the circuit had resets, the tableau is just the stabilizer state at the end.
    # The synthesis creates a circuit that prepares that state from |0>.
    # If the resulting circuit has reset gates, it means it's resetting qubits.
    # But we want a unitary circuit if possible (or at least one that doesn't use mid-circuit measurements/resets if not needed).
    # 'graph_state' produces a circuit that prepares the state from |0> using Cliffords.
    # So it should be fine.
    
    # One catch: The baseline might be a unitary acting on |0>.
    # If we want a circuit that maps |0> to the target state, tableau.to_circuit() does exactly that.
    
    with open("candidate.stim", "w") as f:
        f.write(str(candidate))
        
    print("Done.")

if __name__ == "__main__":
    solve()
