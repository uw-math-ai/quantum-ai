import stim
import sys

def check_commutativity(filename):
    try:
        with open(filename, 'r') as f:
            lines = [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        print(f"File not found: {filename}")
        return

    stabilizers = []
    for line in lines:
        try:
            stabilizers.append(stim.PauliString(line))
        except Exception as e:
            print(f"Error parsing line: {line} - {e}")
            return

    num_stabilizers = len(stabilizers)
    print(f"Loaded {num_stabilizers} stabilizers.")
    
    # Check if they commute
    anticommuting_pairs = []
    for i in range(num_stabilizers):
        for j in range(i + 1, num_stabilizers):
            if not stabilizers[i].commutes(stabilizers[j]):
                anticommuting_pairs.append((i, j))

    if not anticommuting_pairs:
        print("All stabilizers commute.")
        
        # Check independence
        try:
            t = stim.Tableau.from_stabilizers(stabilizers, allow_redundant=True, allow_underconstrained=True)
            print("Stabilizers are consistent and can form a Tableau.")
            if len(t) == len(stabilizers):
                print("Number of stabilizers matches tableau length (if n=n).")
            else:
                 print(f"Tableau length: {len(t)}")
        except Exception as e:
            print(f"Error forming Tableau: {e}")

    else:
        print(f"Found {len(anticommuting_pairs)} anticommuting pairs.")
        for i, j in anticommuting_pairs[:10]:
            print(f"  {i} and {j} anticommute")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        filename = sys.argv[1]
    else:
        filename = "C:\\Users\\anpaz\\Repos\\quantum-ai\\rq1\\data\\gemini-3-pro-preview\\agent_files\\stabilizers_56.txt"
    check_commutativity(filename)
