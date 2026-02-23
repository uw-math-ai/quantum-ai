import sys

try:
    import stim
    print("Stim is installed")
except ImportError:
    print("Stim is NOT installed")
    sys.exit(0)

def analyze_stabilizers(filename):
    with open(filename, 'r') as f:
        lines = [l.strip() for l in f if l.strip()]
    
    print(f"Number of stabilizers: {len(lines)}")
    if not lines:
        return

    num_qubits = len(lines[0])
    print(f"Number of qubits: {num_qubits}")
    
    try:
        # Create a tableau from the stabilizers
        # Note: from_stabilizers returns a Tableau that has these stabilizers.
        # It corresponds to a Clifford operation C such that C |0> has these stabilizers.
        # The circuit for C is what we want.
        t = stim.Tableau.from_stabilizers(lines, allow_redundant=True, allow_underconstrained=True)
        print(f"Successfully created Tableau.")
        
        # Check if we have enough independent stabilizers
        # We can convert to a circuit
        c = t.to_circuit("mp") # "mp" might be measurement or preparation? 
        # Actually without arguments it gives the Clifford operation.
        # The argument method is for how to decompose it. "elimination" is usually good.
        
        print(f"Circuit generated with {len(c)} instructions.")
        
        # Save circuit to a file
        with open("data/gemini-3-pro-preview/agent_files/circuit_candidate.stim", "w") as f:
            f.write(str(c))
            
    except Exception as e:
        print(f"Error creating Tableau/Circuit: {e}")

if __name__ == "__main__":
    analyze_stabilizers("data/gemini-3-pro-preview/agent_files/stabilizers_81.txt")
