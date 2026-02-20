import stim
import sys

def solve():
    with open(r'C:\Users\anpaz\Repos\quantum-ai\rq1\data\gemini-3-pro-preview\agent_files\stabilizers_92.txt', 'r') as f:
        lines = [l.strip() for l in f if l.strip()]

    print(f"Loaded {len(lines)} stabilizers")
    
    # Check string lengths
    lengths = [len(l) for l in lines]
    if len(set(lengths)) != 1:
        print(f"Error: Stabilizers have different lengths: {set(lengths)}")
        for i, l in enumerate(lines):
            if len(l) != 92:
                print(f"  Stabilizer {i} has length {len(l)}")
        # return
    
    num_qubits = lengths[0]
    print(f"Number of qubits: {num_qubits}")
    
    # Create PauliStrings
    stabilizers = [stim.PauliString(l) for l in lines]
    
    # Check commutativity
    anticommuting_pairs = []
    for i in range(len(stabilizers)):
        for j in range(i + 1, len(stabilizers)):
            if stabilizers[i].commutes(stabilizers[j]) == False:
                anticommuting_pairs.append((i, j))
                
    if anticommuting_pairs:
        print(f"Found {len(anticommuting_pairs)} anticommuting pairs!")
        for i, j in anticommuting_pairs[:10]:
            print(f"  {i} vs {j}")
            # print(f"  {lines[i]}")
            # print(f"  {lines[j]}")
    else:
        print("All stabilizers commute.")
        
    # Attempt to solve
    try:
        tableau = stim.Tableau.from_stabilizers(stabilizers, allow_underconstrained=True)
        circuit = tableau.to_circuit("elimination")
        print("Successfully generated circuit with stim.Tableau.from_stabilizers")
        
        # Verify
        sim = stim.TableauSimulator()
        sim.do(circuit)
        
        failed = False
        for i, s in enumerate(stabilizers):
            res = sim.measure_observable(s)
            if res != 0: # 0 means +1 eigenvalue, 1 means -1 eigenvalue
                print(f"Stabilizer {i} failed verification (result {res})")
                failed = True
                
        if not failed:
            print("Circuit verified locally!")
            with open(r'C:\Users\anpaz\Repos\quantum-ai\rq1\data\gemini-3-pro-preview\agent_files\circuit_92.stim', 'w') as f:
                f.write(str(circuit))
        else:
            print("Circuit failed local verification.")

    except Exception as e:
        print(f"Error generating circuit: {e}")

if __name__ == "__main__":
    solve()
