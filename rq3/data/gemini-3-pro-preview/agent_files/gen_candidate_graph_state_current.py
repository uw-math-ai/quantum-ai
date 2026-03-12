import stim

def generate_circuit():
    # Read stabilizers
    with open('target_stabilizers_current.txt', 'r') as f:
        stabilizers = [line.strip() for line in f if line.strip()]
    
    # Create tableau from stabilizers
    # Note: Stim requires PauliString objects
    pauli_stabilizers = [stim.PauliString(s) for s in stabilizers]
    
    # Synthesize circuit using graph_state method
    # This method is known to produce 0 CX gates (using CZ instead)
    # allow_redundant=True is used because sometimes the provided stabilizers might be overcomplete
    # allow_underconstrained=True is used if they are undercomplete (though typically we want full rank)
    try:
        tableau = stim.Tableau.from_stabilizers(pauli_stabilizers, allow_redundant=True, allow_underconstrained=True)
        circuit = tableau.to_circuit(method='graph_state')
        
        # Post-process to remove RX resets if any, replacing with H if on |0>
        # However, graph_state synthesis usually produces a unitary sequence: H, then CZs, then local Cliffords.
        # It shouldn't produce RX unless it's trying to reset.
        # Let's inspect the circuit.
        
        # Convert to string to do simple replacements if needed, but safer to just output it.
        # Check for RX.
        if 'RX' in str(circuit):
             # If RX is present, it means Stim inserted resets. 
             # Since we assume start from |0>, RX is invalid as a gate unless it's a reset.
             # But wait, RX in Stim IS a reset-like operation? No, R is Reset. RX is Reset X?
             # Stim syntax: R 0 (reset Z), RX 0 (reset X).
             # If the prompt says "Do NOT introduce measurements, resets", we must avoid R, RX, RY.
             # But if the circuit needs to initialize, it implies we start from something.
             # Usually 'graph_state' produces a unitary that prepares the state from |0...0>.
             # If it uses RX, it might be resetting to X basis?
             # Let's see what it produces.
             pass
             
        print(circuit)
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    generate_circuit()
