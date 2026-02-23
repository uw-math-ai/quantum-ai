import stim
import sys

def solve():
    # Read stabilizers from file
    with open(r'C:\Users\anpaz\Repos\quantum-ai\rq1\data\gemini-3-pro-preview\agent_files\stabilizers_v2.txt', 'r') as f:
        stabilizers = [line.strip() for line in f if line.strip()]

    num_qubits = 196
    
    # Check if we have enough stabilizers
    print(f'Number of stabilizers: {len(stabilizers)}')
    print(f'Number of qubits: {num_qubits}')
    
    # Check if generators are independent and consistent
    try:
        # Convert strings to PauliStrings
        stim_stabilizers = [stim.PauliString(s) for s in stabilizers]
        
        tableau = stim.Tableau.from_stabilizers(stim_stabilizers, allow_underconstrained=True)
        circuit = tableau.to_circuit()
        
        # Verify
        sim = stim.TableauSimulator()
        sim.do_circuit(circuit)
        
        all_good = True
        for i, s in enumerate(stabilizers):
            if sim.peek_observable_expectation(stim.PauliString(s)) != 1:
                print(f'Stabilizer {i} not satisfied: {s}')
                all_good = False
                break
        
        if all_good:
            print('SUCCESS: Circuit found and verified locally.')
            with open(r'C:\Users\anpaz\Repos\quantum-ai\rq1\data\gemini-3-pro-preview\agent_files\circuit.stim', 'w') as f:
                f.write(str(circuit))
        else:
            print('FAILURE: Circuit generated but does not satisfy stabilizers.')
            
    except Exception as e:
        print(f'ERROR: {e}')

if __name__ == '__main__':
    solve()
