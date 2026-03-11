import stim

def check():
    with open("target_stabilizers_v2.txt", "r") as f:
        lines = [l.strip() for l in f if l.strip()]
    
    print(f"Number of lines: {len(lines)}")
    
    # Check if they are valid Pauli strings
    paulis = []
    for l in lines:
        try:
            paulis.append(stim.PauliString(l))
        except:
            print(f"Invalid line: {l}")
    
    # Create tableau allowing redundancy
    t = stim.Tableau.from_stabilizers(paulis, allow_redundant=True, allow_underconstrained=True)
    print(f"Tableau created successfully with {len(t)} stabilizers (including implicit Z for underconstrained?) No, len(t) is number of qubits usually.")
    
    # Check independence
    # There isn't a direct "rank" method, but from_stabilizers with allow_redundant=False
    # will fail if they are dependent.
    try:
        t_min = stim.Tableau.from_stabilizers(paulis, allow_redundant=False, allow_underconstrained=True)
        print("Stabilizers are independent.")
    except Exception as e:
        print(f"Stabilizers are NOT independent: {e}")

if __name__ == "__main__":
    check()
