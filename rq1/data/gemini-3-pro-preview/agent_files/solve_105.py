import stim
import sys
import os

def read_stabilizers(filename):
    with open(filename, 'r') as f:
        stabs = [line.strip() for line in f if line.strip()]
    return stabs

def solve():
    filename = 'data/gemini-3-pro-preview/agent_files/stabilizers_105.txt'
    # Use absolute path if relative doesn't work, but let's try relative first as per context
    if not os.path.exists(filename):
         filename = r'C:\Users\anpaz\Repos\quantum-ai\rq1\data\gemini-3-pro-preview\agent_files\stabilizers_105.txt'
         
    stabs = read_stabilizers(filename)
    print(f"Loaded {len(stabs)} stabilizers.")
    
    # Check length
    lengths = [len(s) for s in stabs]
    print(f"Stabilizer lengths: {set(lengths)}")
    
    # Convert strings to PauliStrings
    try:
        paulis = [stim.PauliString(s) for s in stabs]
    except Exception as e:
        print(f"Error converting to PauliStrings: {e}")
        return

    # Check for commutativity
    print("Checking commutativity...")
    anticommuting_pairs = []
    for i in range(len(paulis)):
        for j in range(i + 1, len(paulis)):
            if not paulis[i].commutes(paulis[j]):
                anticommuting_pairs.append((i, j))
                
    if anticommuting_pairs:
        print(f"Found {len(anticommuting_pairs)} anticommuting pairs!")
        for i, j in anticommuting_pairs[:10]:
             print(f"  Stab {i} vs Stab {j}")
             # Print the actual stabilizers to debug
             print(f"    {stabs[i]}")
             print(f"    {stabs[j]}")
             
        # If they anticommute, we can't satisfy all of them.
        return

    print("All stabilizers commute.")
    
    try:
        # Create a Tableau from the stabilizers
        # allow_underconstrained=True allows generating a state even if we don't specify N stabilizers for N qubits.
        # We have 105 qubits.
        tableau = stim.Tableau.from_stabilizers(paulis, allow_underconstrained=True)
        
        # Convert to circuit
        circuit = tableau.to_circuit("elimination")
        print("Circuit generated successfully.")
        
        # Verify the number of qubits
        print(f"Circuit num_qubits: {circuit.num_qubits}")
        
        # Output the circuit to a file
        out_file = r'C:\Users\anpaz\Repos\quantum-ai\rq1\data\gemini-3-pro-preview\agent_files\circuit_105.stim'
        with open(out_file, 'w') as f:
            f.write(str(circuit))
        print(f"Wrote circuit to {out_file}")
            
    except Exception as e:
        print(f"Error generating circuit: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    solve()
