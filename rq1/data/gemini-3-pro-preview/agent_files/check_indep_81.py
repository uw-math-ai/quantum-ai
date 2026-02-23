import stim

def check_independence():
    with open(r'C:\Users\anpaz\Repos\quantum-ai\rq1\data\gemini-3-pro-preview\agent_files\stabilizers_81_qubits.txt', 'r') as f:
        lines = [line.strip() for line in f if line.strip()]

    stabilizers = [stim.PauliString(s) for s in lines]
    
    # Create a tableau from all stabilizers
    t_all = stim.Tableau.from_stabilizers(stabilizers, allow_underconstrained=True, allow_redundant=True)
    print(f"Rank with all: {len(t_all) - t_all.num_qubits if 'num_qubits' in dir(t_all) else 'unknown'}") 
    # Actually rank is not directly exposed but we can infer.
    
    # Let's check if the failed ones are redundant.
    # Failed indices: 26 and 35 (0-indexed based on the tool output list order... let me check)
    
    # Tool output order matches input order.
    # 26: IIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIZZIIIIIII
    # 35: IIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIZIZIIIIII
    
    failed_indices = [26, 35]
    failed_stabs = [stabilizers[i] for i in failed_indices]
    
    other_stabs = [s for i, s in enumerate(stabilizers) if i not in failed_indices]
    
    t_others = stim.Tableau.from_stabilizers(other_stabs, allow_underconstrained=True, allow_redundant=True)
    
    # Check if failed_stabs are stabilized by t_others
    sim = stim.TableauSimulator()
    circuit = t_others.to_circuit("elimination")
    sim.do(circuit)
    
    for i, fs in zip(failed_indices, failed_stabs):
        exp = sim.peek_observable_expectation(fs)
        print(f"Stabilizer {i} expectation with others: {exp}")
        if exp == 0:
            print("  -> Independent (or dependent on missing DOF)")
        elif exp == 1:
            print("  -> Redundant and Consistent")
        elif exp == -1:
            print("  -> Redundant and Inconsistent")

if __name__ == "__main__":
    check_independence()
