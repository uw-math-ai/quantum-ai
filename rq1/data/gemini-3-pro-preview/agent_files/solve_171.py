import stim
import sys
import os

def solve_stabilizers(stabilizers_file, output_file):
    with open(stabilizers_file, 'r') as f:
        lines = [line.strip().replace(',', '') for line in f.readlines() if line.strip()]
    
    stabilizers = [stim.PauliString(s) for s in lines]
    n = len(stabilizers[0]) # 171
    print(f"Loaded {len(stabilizers)} stabilizers for {n} qubits.")
    
    # Try to find one more stabilizer to complete the set
    # We try Z_k, then X_k, then Y_k for k in range(n)
    found_completion = False
    completed_stabilizers = []
    
    # We need to find a Pauli string P such that {stabilizers + P} is a valid stabilizer group
    # i.e., P commutes with all existing stabilizers, and is independent.
    # Actually, simpler: just try to construct a Tableau from (stabilizers + P)
    # If it works, great. If not (due to anticommutation or dependence), try next.
    
    candidates = []
    # Try single qubit Paulis
    for k in range(n):
        for p in ['Z', 'X', 'Y']:
            ps = stim.PauliString(n)
            ps[k] = p
            candidates.append(ps)
            
    # Also try products of two? No, single should be enough for 1 missing generator usually.
    
    for cand in candidates:
        try:
            # Check commutativity first to avoid expensive Tableau build if obvious
            # But Tableau build is fast enough for 171 qubits (N^3 ~ 5e6 ops, manageable)
            # Actually commutativity check is N*M, much faster.
            
            # Check if cand commutes with all stabilizers
            commutes = True
            for s in stabilizers:
                if not s.commutes(cand):
                    commutes = False
                    break
            if not commutes:
                continue
                
            # If it commutes, check independence by trying to build tableau
            test_set = stabilizers + [cand]
            tableau = stim.Tableau.from_stabilizers(test_set)
            print(f"Found completing stabilizer: {cand}")
            found_completion = True
            
            # Generate circuit
            # method="elimination" uses Gaussian elimination to find a circuit with H, S, CX, etc.
            circuit = tableau.to_circuit(method="elimination")
            
            with open(output_file, "w") as f:
                f.write(str(circuit))
            print(f"Circuit written to {output_file}")
            return
            
        except Exception as e:
            # Likely dependent
            continue
            
    print("Could not find a completing stabilizer.")

if __name__ == "__main__":
    stabilizers_file = r"C:\Users\anpaz\Repos\quantum-ai\rq1\data\gemini-3-pro-preview\agent_files\stabilizers_171.txt"
    output_file = r"C:\Users\anpaz\Repos\quantum-ai\rq1\data\gemini-3-pro-preview\agent_files\circuit_171.stim"
    solve_stabilizers(stabilizers_file, output_file)
