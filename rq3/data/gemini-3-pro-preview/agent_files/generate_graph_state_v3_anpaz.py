import stim

def main():
    # Read stabilizers
    with open('target_stabilizers_anpaz.txt', 'r') as f:
        lines = [l.strip() for l in f if l.strip()]

    # Convert to PauliStrings
    stabilizers = [stim.PauliString(l) for l in lines]

    # Create Tableau
    try:
        t = stim.Tableau.from_stabilizers(stabilizers, allow_redundant=True, allow_underconstrained=True)
    except Exception as e:
        print(f"Error creating tableau: {e}")
        return

    # Synthesize circuit using graph state method
    circuit = t.to_circuit(method='graph_state')

    # Convert to string
    circuit_str = str(circuit)

    # Post-processing:
    # 1. Replace RX with H if it appears at the beginning (graph state synthesis might use it)
    #    RX is not a standard gate in some contexts, but let's see what Stim produces.
    #    Stim usually produces H, S, CZ, X, Y, Z.
    #    If it produces R (Reset), we might want to avoid it if not allowed.
    #    But let's first see what it produces.
    
    # 2. Decompose CZ into CX if necessary?
    #    If cx_count only counts CX, then keeping CZ is better (cx_count=0).
    #    If CZ is not allowed, we need to decompose.
    #    But usually Stim circuits allow CZ.
    
    # Check for RX/R
    lines = circuit_str.splitlines()
    new_lines = []
    for line in lines:
        if line.strip().startswith('RX'):
            # Replace RX with H
            # RX target -> H target
            parts = line.split()
            targets = parts[1:]
            new_lines.append(f"H {' '.join(targets)}")
        elif line.strip().startswith('R '): # Reset Z
             # If reset is not allowed, we might remove it if we assume |0> input.
             # But let's assume graph_state produces unitary ops mostly.
             pass
        else:
            new_lines.append(line)
            
    final_circuit = '\n'.join(new_lines)
    
    # Print the raw circuit to stdout
    print(final_circuit)

if __name__ == '__main__':
    main()
