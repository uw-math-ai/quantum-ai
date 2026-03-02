import stim

def check_dependence():
    with open(r'C:\Users\anpaz\Repos\quantum-ai\rq1\data\gemini-3-pro-preview\agent_files\my_stabilizers_72.txt', 'r') as f:
        stabilizers = [line.strip() for line in f if line.strip()]
    
    paulis = [stim.PauliString(s) for s in stabilizers]
    
    # Try to add them one by one to a tableau to see if they are independent
    tableau = stim.Tableau(72)
    # This is not trivial to check with just Tableau constructor.
    # But Tableau.from_stabilizers should handle dependent stabilizers if they are consistent.
    # If they are dependent but INCONSISTENT (i.e. product is -I), then it fails or drops one.
    
    # Let's check consistency of dependent ones.
    # We can do Gaussian elimination manually or use stim.TableauSimulator?
    # No, let's use Tableau.from_stabilizers and see if it raises an error without allow_underconstrained?
    # Or just check if the resulting tableau satisfies all stabilizers.
    
    tableau = stim.Tableau.from_stabilizers(paulis, allow_underconstrained=True)
    
    # Check each stabilizer against the tableau
    all_good = True
    for i, p in enumerate(paulis):
        # The tableau stabilizes the state |psi>. 
        # So P|psi> should be +|psi>.
        # This means P * T should result in a +1 phase for the stabilized observables?
        # A simpler check: 
        # T^-1 * P * T should be a Z operator on an ancilla or Identity?
        # Actually, for a stabilizer state stabilized by Z_i (in the standard basis),
        # converting P to the destabilized basis should result in a product of Z_i's.
        
        # Or even simpler: measure the stabilizer on the state prepared by the tableau.
        # It should be deterministic +1.
        
        # Let's simulate the circuit and measure the stabilizers.
        sim = stim.TableauSimulator()
        sim.do_tableau(tableau, [k for k in range(72)])
        res = sim.measure_observable(p)
        if res != False: # False means +1 eigenvalue (measurement result 0), True means -1 eigenvalue (measurement result 1)
             print(f"Stabilizer {i} not satisfied: {p}")
             all_good = False
             
    if all_good:
        print("All stabilizers satisfied by the tableau.")

if __name__ == "__main__":
    check_dependence()
