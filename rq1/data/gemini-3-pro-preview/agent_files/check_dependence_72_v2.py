import stim

def check_dependence():
    try:
        with open(r'C:\Users\anpaz\Repos\quantum-ai\rq1\data\gemini-3-pro-preview\agent_files\my_stabilizers_72.txt', 'r') as f:
            stabilizers = [line.strip() for line in f if line.strip()]
        
        paulis = [stim.PauliString(s) for s in stabilizers]
        
        tableau = stim.Tableau.from_stabilizers(paulis, allow_underconstrained=True)
        print(f"Tableau len: {len(tableau)}")
        
        sim = stim.TableauSimulator()
        sim.do_tableau(tableau, list(range(len(tableau))))
        
        all_good = True
        for i, p in enumerate(paulis):
            res = sim.measure_observable(p)
            if res:
                print(f"Stabilizer {i} NOT satisfied: {stabilizers[i]}")
                all_good = False
        
        if all_good:
            print("All stabilizers satisfied by the tableau.")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_dependence()
