import stim

def check_dependence():
    with open(r"C:\Users\anpaz\Repos\quantum-ai\rq1\data\gemini-3-pro-preview\agent_files\stabilizers_135.txt", 'r') as f:
        lines = [line.strip() for line in f if line.strip()]
        
    # Check if the failing stabilizer is dependent on others
    # Failing: line 62 (index 61)
    target = lines[61]
    others = lines[:61] + lines[62:]
    
    t_others = stim.Tableau.from_stabilizers([stim.PauliString(s) for s in others], allow_redundant=True, allow_underconstrained=True)
    
    # Check if target is in the group
    # We can check if target commutes with the tableau stabilizers? No.
    # We can check if adding it increases the number of stabilizers?
    
    t_all = stim.Tableau.from_stabilizers([stim.PauliString(s) for s in lines], allow_redundant=True, allow_underconstrained=True)
    
    print(f"Others independent count: {len(t_others)}")
    print(f"All independent count: {len(t_all)}")
    
    if len(t_all) == len(t_others):
        print("Target IS dependent on others.")
    else:
        print("Target is INDEPENDENT.")

if __name__ == "__main__":
    check_dependence()
