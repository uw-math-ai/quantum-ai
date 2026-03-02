import stim
import sys

def solve():
    try:
        with open(r"C:\Users\anpaz\Repos\quantum-ai\rq1\data\gemini-3-pro-preview\agent_files\stabs_54.txt", "r") as f:
            lines = [l.strip() for l in f if l.strip()]
    except FileNotFoundError:
        print("Error: Input file not found.")
        return

    print(f"Loaded {len(lines)} stabilizers.")
    
    # Convert to stim.PauliString
    stabilizers = []
    for line in lines:
        try:
            stabilizers.append(stim.PauliString(line))
        except Exception as e:
            print(f"Error parsing line '{line}': {e}")
            return

    # Check number of qubits
    if not stabilizers:
        print("No stabilizers found.")
        return

    n_qubits = len(stabilizers[0])
    print(f"Number of qubits: {n_qubits}")
    
    # Verify commutativity
    print("Checking commutativity...")
    all_commute = True
    for i in range(len(stabilizers)):
        for j in range(i + 1, len(stabilizers)):
            if not stabilizers[i].commutes(stabilizers[j]):
                print(f"Stabilizers {i} and {j} do not commute!")
                print(f"{i}: {stabilizers[i]}")
                print(f"{j}: {stabilizers[j]}")
                all_commute = False
                
    if not all_commute:
        print("Not all stabilizers commute. Cannot form a valid stabilizer state.")
        return

    print("All stabilizers commute.")

    # Try to generate tableau
    try:
        tableau = stim.Tableau.from_stabilizers(stabilizers, allow_underconstrained=True)
        print("Tableau created successfully.")
        
        # Convert to circuit
        circuit = tableau.to_circuit("elimination")
        print("Circuit generated successfully.")
        
        with open("circuit_54.stim", "w") as f:
            f.write(str(circuit))
            
        print("Circuit saved to circuit_54.stim")
        
    except Exception as e:
        print(f"Error generating tableau/circuit: {e}")

if __name__ == "__main__":
    solve()
