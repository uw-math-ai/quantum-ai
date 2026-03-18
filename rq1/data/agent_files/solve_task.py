import stim

def solve():
    stabilizers = [
        "XZZXI",
        "IXZZX",
        "XIXZZ",
        "ZXIXZ",
        "ZZZZZ"
    ]
    
    # Check commutativity
    def commute(s1, s2):
        anti = 0
        for c1, c2 in zip(s1, s2):
            if c1 != 'I' and c2 != 'I' and c1 != c2:
                anti += 1
        return anti % 2 == 0

    print("Checking commutativity...")
    for i in range(len(stabilizers)):
        for j in range(i + 1, len(stabilizers)):
            if not commute(stabilizers[i], stabilizers[j]):
                print(f"Warning: {stabilizers[i]} and {stabilizers[j]} anti-commute!")
            else:
                pass # print(f"{stabilizers[i]} and {stabilizers[j]} commute.")

    # Try to create tableau
    try:
        t = stim.Tableau.from_stabilizers([stim.PauliString(s) for s in stabilizers])
        print("Tableau created successfully.")
        
        # Convert to circuit
        # method="graph_state" is usually good for preparing stabilizer states from |0>
        circ = t.to_circuit(method="graph_state")
        print("Circuit generated.")
        print(circ)
        
        # Save to file
        with open("candidate.stim", "w") as f:
            f.write(str(circ))
            
    except Exception as e:
        print(f"Error creating tableau: {e}")

if __name__ == "__main__":
    solve()
