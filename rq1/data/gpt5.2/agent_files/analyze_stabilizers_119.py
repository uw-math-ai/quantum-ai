import stim
import os

def load_stabilizers(filename):
    if not os.path.exists(filename):
        print(f"File {filename} not found.")
        return []
    with open(filename, 'r') as f:
        lines = [line.strip() for line in f if line.strip()]
    return lines

def analyze():
    filename = r'data\gemini-3-pro-preview\agent_files\stabilizers_119.txt'
    lines = load_stabilizers(filename)
    if not lines:
        return
        
    stabilizers = []
    for s in lines:
        # stim.PauliString(s) expects valid Pauli string
        try:
            p = stim.PauliString(s)
            stabilizers.append(p)
        except ValueError as e:
            print(f"Invalid stabilizer {s}: {e}")
            
    print(f"Number of valid stabilizers: {len(stabilizers)}")
    if not stabilizers:
        return
        
    # Check lengths
    lengths = [len(s) for s in stabilizers]
    if len(set(lengths)) > 1:
        print(f"Error: Stabilizers have different lengths: {set(lengths)}")
        return
    else:
        print(f"All stabilizers have length: {lengths[0]}")
        
    num_qubits = lengths[0]
    
    # Check commutativity
    anticommuting_pairs = []
    for i in range(len(stabilizers)):
        for j in range(i + 1, len(stabilizers)):
            if not stabilizers[i].commutes(stabilizers[j]):
                anticommuting_pairs.append((i, j))
                
    if anticommuting_pairs:
        print(f"Found {len(anticommuting_pairs)} anticommuting pairs.")
        for idx, (i, j) in enumerate(anticommuting_pairs[:5]):
            print(f"  {i} vs {j}: {lines[i]} vs {lines[j]}")
    else:
        print("All stabilizers commute.")
        
        # Check independence
        try:
            # allow_overconstrained allows for dependent stabilizers IF they are consistent
            # But stim.Tableau.from_stabilizers creates a Tableau T such that T|0> is stabilized by the provided stabilizers.
            # If stabilizers are redundant, stim might complain unless we are careful.
            # `stim.Tableau.from_stabilizers` returns a tableau that prepares the state.
            # If the stabilizers are not independent (but consistent), it picks a valid state.
            # If they are inconsistent (e.g. +Z and -Z), it fails.
            
            tableau = stim.Tableau.from_stabilizers(stabilizers, allow_redundant=True, allow_underconstrained=True)
            print("Successfully created tableau from stabilizers (redundancy allowed).")
            
            # Count independent generators
            # We can convert back to stabilizers and see how many we get? No.
            # The tableau has N qubits. It defines N stabilizers.
            # The input might be fewer or more.
            
            # If we want to check for independence, we can row-reduce.
            # But let's just use the tableau to generate the circuit if possible.
            
            circuit = tableau.to_circuit()
            print(f"Circuit generated successfully. Instructions: {len(circuit)}")
            
        except ValueError as e:
            print(f"Failed to create tableau: {e}")

if __name__ == "__main__":
    analyze()
