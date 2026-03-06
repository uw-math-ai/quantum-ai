import stim
import sys

def check_stabilizers(circuit, stabilizers):
    sim = stim.TableauSimulator()
    sim.do(circuit)
    
    preserved = 0
    total = len(stabilizers)
    
    for s_str in stabilizers:
        try:
            s = stim.PauliString(s_str)
            if sim.peek_observable_expectation(s) == 1:
                preserved += 1
        except Exception as e:
            # print(f'Error checking stabilizer {s_str}: {e}')
            pass
            
    return preserved, total

def count_cx(circuit):
    count = 0
    for instr in circuit:
        if instr.name == 'CX' or instr.name == 'CNOT':
            count += len(instr.targets_copy()) // 2
    return count

def get_volume(circuit):
    count = 0
    for instr in circuit:
        if instr.name in ['CX', 'CY', 'CZ', 'H', 'S', 'SQRT_X', 'SQRT_Y', 'SQRT_Z', 'X', 'Y', 'Z', 'I', 'SWAP', 'ISWAP', 'SQRT_XX', 'SQRT_YY', 'SQRT_ZZ']:
             if instr.name in ['CX', 'CY', 'CZ', 'SWAP', 'ISWAP', 'SQRT_XX', 'SQRT_YY', 'SQRT_ZZ']:
                 count += len(instr.targets_copy()) // 2
             else:
                 count += len(instr.targets_copy())
    return count

def analyze():
    try:
        # Check if candidate exists
        try:
            with open('candidate_graph.stim', 'r') as f:
                circuit_text = f.read()
            circuit = stim.Circuit(circuit_text)
            print('Loaded candidate_graph.stim')
        except:
            print('Could not load candidate_graph.stim')
            return

        with open('target_stabilizers.txt', 'r') as f:
            stabilizers = [line.strip().replace(',', '') for line in f if line.strip()]
            
        preserved, total = check_stabilizers(circuit, stabilizers)
        cx = count_cx(circuit)
        vol = get_volume(circuit)
        
        print(f'Candidate Stabilizers preserved: {preserved}/{total}')
        print(f'Candidate CX count: {cx}')
        print(f'Candidate Volume: {vol}')
        
        if preserved == total:
            print('VALID: Preserves all stabilizers.')
        else:
            print('INVALID: Does not preserve all stabilizers.')
            
    except Exception as e:
        print(f'Error: {e}')
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    analyze()
