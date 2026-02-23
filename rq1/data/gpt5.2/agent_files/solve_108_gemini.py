import stim
import sys

def solve():
    # Read stabilizers
    with open(r'C:\Users\anpaz\Repos\quantum-ai\rq1\data\gemini-3-pro-preview\agent_files\stabilizers_108.txt', 'r') as f:
        stabilizers_strings = [line.strip() for line in f if line.strip()]
    stabilizers = [stim.PauliString(s) for s in stabilizers_strings]

    print(f"Loaded {len(stabilizers)} stabilizers.")
    
    # Create tableau from stabilizers
    try:
        # allow_underconstrained=True allows finding a state that satisfies these, 
        # even if it's not a unique state (e.g. fewer than N stabilizers).
        tableau = stim.Tableau.from_stabilizers(stabilizers, allow_underconstrained=True)
        print("Successfully created tableau.")
    except Exception as e:
        print(f"Error creating tableau: {e}")
        return

    # Convert to circuit
    # The tableau represents the operation U such that U|0> = |stabilizer_state>
    circuit = tableau.to_circuit()
    
    # Stim's to_circuit might use complex gates like MPP, but for a state preparation 
    # it usually outputs a circuit of single qubit gates and CNOTs/CZs if possible, 
    # or just a general Clifford circuit.
    # The prompt asks for a "valid Stim circuit".
    
    with open(r'C:\Users\anpaz\Repos\quantum-ai\rq1\data\gemini-3-pro-preview\agent_files\circuit_108.stim', 'w') as f:
        f.write(str(circuit))
        
    print("Circuit generated and saved to circuit_108.stim.")

if __name__ == "__main__":
    solve()
