import stim

def check_consistency():
    with open(r"C:\Users\anpaz\Repos\quantum-ai\rq1\data\gemini-3-pro-preview\agent_files\stabilizers_153.txt", "r") as f:
        lines = [line.strip() for line in f if line.strip()]

    paulis = [stim.PauliString(s) for s in lines]
    
    # Check for independence by adding them one by one
    t = stim.Tableau(153)
    # This is not quite right. Stim doesn't have a direct "check independence" function easily accessible this way.
    # But we can try to create a tableau from them.
    
    try:
        t = stim.Tableau.from_stabilizers(paulis)
        print("Tableau creation SUCCESS")
        # Check if the tableau actually stabilizes the inputs
        # We can do this by measuring each stabilizer on the tableau state
        # Or simply by checking commutation.
        
        # But wait, to_circuit() generates a circuit that prepares the state.
        # If the state is correct, then circuit is correct.
        
        # Let's check if the stabilizers commute with each other.
        for i in range(len(paulis)):
            for j in range(i + 1, len(paulis)):
                if not paulis[i].commutes(paulis[j]):
                    print(f"Stabilizers {i} and {j} do NOT commute!")
                    return

        print("All stabilizers commute.")
        
    except Exception as e:
        print(f"Tableau creation FAILED: {e}")

if __name__ == "__main__":
    check_consistency()
