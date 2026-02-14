import stim
import sys

def analyze():
    with open("target_stabilizers_72.txt", "r") as f:
        lines = [l.strip() for l in f if l.strip()]

    # Parse stabilizers
    stabilizers = []
    for i, line in enumerate(lines):
        try:
            # remove line numbers if present "1. XIX..."
            if ". " in line[:5]:
                line = line.split(". ", 1)[1]
            stabilizers.append(stim.PauliString(line))
        except Exception as e:
            print(f"Error parsing line {i+1}: {line}")
            print(e)
            return

    num_qubits = len(stabilizers[0])
    print(f"Num qubits: {num_qubits}")
    print(f"Num stabilizers: {len(stabilizers)}")

    # Check commutation
    anticommuting_pairs = []
    for i in range(len(stabilizers)):
        for j in range(i + 1, len(stabilizers)):
            if stabilizers[i].commutes(stabilizers[j]) == False:
                anticommuting_pairs.append((i, j))
    
    if anticommuting_pairs:
        print(f"Found {len(anticommuting_pairs)} anticommuting pairs!")
        for p in anticommuting_pairs[:5]:
            print(f"  {p}: {stabilizers[p[0]]} vs {stabilizers[p[1]]}")
    else:
        print("All stabilizers commute.")

    # Check independence (rank)
    # We can use Gaussian elimination to find the rank.
    # Or just try to construct a Tableau from them, stim might complain if redundant.
    
    # Let's use Tableau.from_stabilizers if possible, but we need to pick independent ones.
    # To do that, we can use tableau logic.
    
    # Convert to boolean matrix (2*n columns for X and Z)
    # This is a bit manual, but reliable.
    
    # Or try adding them one by one to a Tableau until full.
    
    sim = stim.TableauSimulator()
    # Actually, let's just use the tableau method from stim if available or build it.
    
    # If they all commute, we can find a generating set.
    
if __name__ == "__main__":
    analyze()
