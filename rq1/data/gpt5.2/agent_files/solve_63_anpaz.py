import stim
import numpy as np

def load_stabilizers(filename):
    with open(filename, 'r') as f:
        lines = [line.strip() for line in f if line.strip()]
    return lines

def check_commutativity(stabilizers):
    n = len(stabilizers[0])
    num_stabs = len(stabilizers)
    
    xs = np.zeros((num_stabs, n), dtype=int)
    zs = np.zeros((num_stabs, n), dtype=int)
    
    for i, s in enumerate(stabilizers):
        for j, char in enumerate(s):
            if char == 'X':
                xs[i, j] = 1
            elif char == 'Z':
                zs[i, j] = 1
            elif char == 'Y':
                xs[i, j] = 1
                zs[i, j] = 1
                
    comm_matrix = (np.matmul(xs, zs.T) + np.matmul(zs, xs.T)) % 2
    
    anticommuting_pairs = []
    for i in range(num_stabs):
        for j in range(i + 1, num_stabs):
            if comm_matrix[i, j] == 1:
                anticommuting_pairs.append((i, j))
                
    return anticommuting_pairs

def solve():
    filename = "data/gemini-3-pro-preview/agent_files/stabilizers_63_task.txt"
    try:
        stabilizers = load_stabilizers(filename)
    except FileNotFoundError:
        print(f"File {filename} not found.")
        return

    print(f"Loaded {len(stabilizers)} stabilizers.")
    if not stabilizers:
        print("No stabilizers found.")
        return

    print(f"Length of first stabilizer: {len(stabilizers[0])}")
    
    anticommuting = check_commutativity(stabilizers)
    if anticommuting:
        print(f"Found {len(anticommuting)} anticommuting pairs!")
        for i, j in anticommuting[:10]:
            print(f"  {i} and {j} anticommute")
            print(f"  S{i}: {stabilizers[i]}")
            print(f"  S{j}: {stabilizers[j]}")
        return
    else:
        print("All stabilizers commute.")
    
    try:
        # allow_underconstrained=True because we have 62 stabilizers for 63 qubits
        tableau = stim.Tableau.from_stabilizers([stim.PauliString(s) for s in stabilizers], allow_underconstrained=True)
        print("Successfully created tableau.")
        circuit = tableau.to_circuit()
        
        with open("data/gemini-3-pro-preview/agent_files/circuit_63_anpaz.stim", "w") as f:
            f.write(str(circuit))
        print("Circuit saved to data/gemini-3-pro-preview/agent_files/circuit_63_anpaz.stim")
        
        # Verify
        print("Verifying circuit...")
        sim = stim.TableauSimulator()
        sim.do_circuit(circuit)
        
        failed = False
        for i, s in enumerate(stabilizers):
            p = stim.PauliString(s)
            res = sim.peek_observable_expectation(p)
            if res != 1:
                print(f"Stabilizer {i} failed: {s} -> {res}")
                failed = True
                
        if not failed:
            print("VERIFICATION SUCCESS: Circuit satisfies all stabilizers.")
        else:
            print("VERIFICATION FAILED.")
            
    except Exception as e:
        print(f"Error creating tableau: {e}")

if __name__ == "__main__":
    solve()
