import stim
import sys

def parse_stabilizers(filename):
    with open(filename, 'r') as f:
        lines = [line.strip() for line in f if line.strip()]
    return lines

def solve():
    print("Parsing stabilizers...")
    try:
        stabilizers = parse_stabilizers("stabilizers_54.txt")
    except FileNotFoundError:
        print("stabilizers_54.txt not found.")
        sys.exit(1)

    print(f"Loaded {len(stabilizers)} stabilizers.")
    
    ps = []
    for s in stabilizers:
        try:
            ps.append(stim.PauliString(s))
        except Exception as e:
            print(f"Invalid stabilizer string: {s}")
            sys.exit(1)
    
    print("Generating tableau...")
    try:
        tableau = stim.Tableau.from_stabilizers(ps, allow_underconstrained=True)
    except Exception as e:
        print(f"Failed to create tableau from stabilizers: {e}")
        sys.exit(1)
    
    print("Converting to circuit...")
    try:
        circuit = tableau.to_circuit("elimination")
    except Exception as e:
        print(f"Failed to convert tableau to circuit: {e}")
        sys.exit(1)
    
    print("Verifying locally...")
    sim = stim.TableauSimulator()
    sim.do(circuit)
    
    valid = True
    for i, p in enumerate(ps):
        if sim.measure_observable(p):
            print(f"Stabilizer {i} failed: measured -1")
            valid = False
    
    if valid:
        print("Circuit found and verified locally.")
        with open("circuit_54.stim", "w") as f:
            f.write(str(circuit))
    else:
        print("Circuit found but failed verification.")

if __name__ == "__main__":
    solve()
