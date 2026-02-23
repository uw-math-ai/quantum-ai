import stim
import sys

def solve():
    with open("C:/Users/anpaz/Repos/quantum-ai/rq1/stabilizers_161_new.txt", "r") as f:
        content = f.read()
    
    parts = content.replace('\n', ',').split(',')
    
    stabilizers = [p.strip() for p in parts if p.strip()]
    
    print(f"Found {len(stabilizers)} stabilizers.")
    
    try:
        pauli_strings = [stim.PauliString(s) for s in stabilizers]
    except Exception as e:
        print(f"Error parsing stabilizers: {e}")
        return

    if pauli_strings:
        print(f"Length of first stabilizer: {len(pauli_strings[0])}")

    try:
        tableau = stim.Tableau.from_stabilizers(pauli_strings, allow_underconstrained=True, allow_redundant=True)
    except Exception as e:
        print(f"Error creating tableau: {e}")
        return

    circuit = tableau.to_circuit("elimination")
    
    with open("C:/Users/anpaz/Repos/quantum-ai/rq1/circuit_161.stim", "w") as f:
        f.write(str(circuit))
        
    print("Circuit generated and saved to circuit_161.stim")

if __name__ == "__main__":
    solve()
