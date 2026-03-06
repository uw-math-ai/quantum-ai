import stim
import sys

def load_stabilizers(filename):
    with open(filename, 'r') as f:
        lines = [line.strip() for line in f if line.strip()]
    return lines

def main():
    filename = r'C:\Users\anpaz\Repos\quantum-ai\rq1\data\gemini-3-pro-preview\agent_files\stabilizers.txt'
    stabilizers = load_stabilizers(filename)
    
    print(f"Loaded {len(stabilizers)} stabilizers.")
    
    # Create a tableau from the stabilizers
    # allow_redundant=True is needed because analyze_stabs.py reported redundancy
    # allow_underconstrained=True is needed because 74 < 75 (and rank might be even lower)
    try:
        t = stim.Tableau.from_stabilizers(
            [stim.PauliString(s) for s in stabilizers], 
            allow_redundant=True, 
            allow_underconstrained=True
        )
        print("Successfully created tableau.")
        print(f"Rank: {len(t)}")
        
        # Convert to circuit
        circuit = t.to_circuit(method="elimination")
        print("Successfully generated circuit.")
        print(f"Circuit instructions: {len(circuit)}")
        
        # Verify locally
        # Simulate the circuit and measure the stabilizers
        # To verify, we start with |0...0>, run the circuit, and check if the state is stabilized by the generators.
        # However, checking if a state is stabilized by P means P|psi> = |psi>.
        # Alternatively, we can use the tableau to check if the stabilizers are in the stabilizer group of the output state.
        
        # Let's just output the circuit to a file and we can verify it separately or use the tool.
        with open(r'C:\Users\anpaz\Repos\quantum-ai\rq1\data\gemini-3-pro-preview\agent_files\circuit.stim', 'w') as f:
            f.write(str(circuit))
            
    except Exception as e:
        print(f"Error generating circuit: {e}")

if __name__ == "__main__":
    main()
