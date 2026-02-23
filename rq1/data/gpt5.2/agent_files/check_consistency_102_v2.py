import stim

def check_consistency():
    try:
        with open(r"data\gemini-3-pro-preview\agent_files\stabilizers_102.txt", "r") as f:
            lines = [line.strip() for line in f if line.strip()]

        stabilizers = lines
        paulis = [stim.PauliString(s) for s in stabilizers]
        
        print("Creating tableau...")
        tableau = stim.Tableau.from_stabilizers(paulis, allow_underconstrained=True)
        print("Tableau created.")
        
        circuit = tableau.to_circuit()
        sim = stim.TableauSimulator()
        sim.do_circuit(circuit)
        
        failed_indices = []
        for i, p in enumerate(paulis):
            ex = sim.peek_observable_expectation(p)
            if ex != 1:
                print(f"Stabilizer {i} expectation: {ex}")
                failed_indices.append(i)
                
        if not failed_indices:
            print("All stabilizers satisfied by the Stim tableau.")
        else:
            print(f"Failed stabilizers: {failed_indices}")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_consistency()
