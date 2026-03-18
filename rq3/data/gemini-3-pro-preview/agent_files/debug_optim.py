import stim

def debug():
    # Check S tableau
    t_s = stim.Tableau.from_circuit(stim.Circuit("S 0"))
    print(f"S tableau: {t_s}")
    
    # Check S_DAG tableau
    t_sdag = stim.Tableau.from_circuit(stim.Circuit("S_DAG 0"))
    print(f"S_DAG tableau: {t_sdag}")
    
    # Check what table generation does
    # We simulate BFS step
    t_curr = stim.Tableau(1)
    # Apply S
    t_curr.append(t_s, [0])
    print(f"I + S tableau: {t_curr}")
    
    # Apply S_DAG
    t_curr2 = stim.Tableau(1)
    t_curr2.append(t_sdag, [0])
    print(f"I + S_DAG tableau: {t_curr2}")
    
    if str(t_s) == str(t_curr):
        print("Strings match")
    else:
        print("Strings DO NOT match")

if __name__ == "__main__":
    debug()
