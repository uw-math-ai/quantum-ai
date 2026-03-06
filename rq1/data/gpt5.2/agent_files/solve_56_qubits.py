import stim
import numpy as np

def check_commutativity(stabilizers):
    n = len(stabilizers[0])
    m = len(stabilizers)
    
    # Convert to symplectic form
    xs = np.zeros((m, n), dtype=int)
    zs = np.zeros((m, n), dtype=int)
    
    for i, s in enumerate(stabilizers):
        for j, char in enumerate(s):
            if char == 'X':
                xs[i, j] = 1
            elif char == 'Z':
                zs[i, j] = 1
            elif char == 'Y':
                xs[i, j] = 1
                zs[i, j] = 1
                
    # Check commutativity
    anticommuting_pairs = []
    for i in range(m):
        for j in range(i + 1, m):
            comm = np.sum(xs[i] & zs[j]) + np.sum(zs[i] & xs[j])
            if comm % 2 != 0:
                anticommuting_pairs.append((i, j))
                
    if anticommuting_pairs:
        print(f"Found {len(anticommuting_pairs)} anticommuting pairs.")
        return False
    else:
        print("All stabilizers commute.")
        return True

def solve():
    try:
        with open(r"C:\Users\anpaz\Repos\quantum-ai\rq1\data\gemini-3-pro-preview\agent_files\stabilizers_56.txt", 'r') as f:
            lines = [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        print("Stabilizer file not found.")
        return

    print(f"Loaded {len(lines)} stabilizers.")
    
    if not check_commutativity(lines):
        return

    try:
        pauli_strings = [stim.PauliString(s) for s in lines]
        tableau = stim.Tableau.from_stabilizers(pauli_strings, allow_redundant=True, allow_underconstrained=True)
        print("Successfully created tableau from stabilizers!")
        
        circuit = tableau.to_circuit()
        
        print("Circuit generated.")
        
        # Manually write to file, splitting instructions
        with open(r"C:\Users\anpaz\Repos\quantum-ai\rq1\data\gemini-3-pro-preview\agent_files\circuit_56.stim", 'w') as f:
            for op in circuit.flattened():
                if op.name in ["CX", "CZ", "SWAP", "ISWAP", "SQRT_XX", "SQRT_YY", "SQRT_ZZ"]:
                    targets = op.targets_copy()
                    for i in range(0, len(targets), 2):
                        # Construct single gate instruction
                        t1 = targets[i]
                        t2 = targets[i+1]
                        # Handling targets which might be qubits or measurements (but here just qubits)
                        # stim targets can be integers or stim.GateTarget objects.
                        # For simple tableau to circuit, they are usually just qubit indices (integers) 
                        # but stim 1.12+ uses GateTarget.
                        # Let's use str(op) to check format or just reconstruct.
                        
                        # Safer: create a mini circuit for each pair
                        mini_c = stim.Circuit()
                        mini_c.append(op.name, [t1, t2], op.gate_args_copy())
                        f.write(str(mini_c).strip() + "\n")
                elif op.name in ["H", "S", "S_DAG", "X", "Y", "Z", "I", "SQRT_X", "SQRT_X_DAG", "SQRT_Y", "SQRT_Y_DAG", "SQRT_Z", "SQRT_Z_DAG"]:
                     targets = op.targets_copy()
                     for t in targets:
                         mini_c = stim.Circuit()
                         mini_c.append(op.name, [t], op.gate_args_copy())
                         f.write(str(mini_c).strip() + "\n")
                else:
                    # For other gates (measurements etc), just write as is
                    f.write(str(op) + "\n")
            
    except Exception as e:
        print(f"Failed to create tableau: {e}")

if __name__ == "__main__":
    solve()
