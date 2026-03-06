import stim
import sys

def check():
    try:
        print('Loading candidate...')
        with open('candidate_graph.stim', 'r') as f:
            circuit = stim.Circuit(f.read())
            
        print('Loading stabilizers...')
        with open('target_stabilizers.txt', 'r') as f:
            stabilizers = [line.strip().replace(',', '') for line in f if line.strip()]
            
        print(f'Verifying {len(stabilizers)} stabilizers...')
        
        sim = stim.TableauSimulator()
        sim.do(circuit)
        
        preserved = 0
        for i, s_str in enumerate(stabilizers):
            try:
                s = stim.PauliString(s_str)
                if sim.peek_observable_expectation(s) == 1:
                    preserved += 1
                else:
                    pass # print(f'Failed stabilizer {i}')
            except Exception as e:
                print(f'Error on stabilizer {i}: {e}')
                
        print(f'Preserved: {preserved}/{len(stabilizers)}')
        
        # Check metrics
        cx = 0
        vol = 0
        for instr in circuit:
            if instr.name == 'CX' or instr.name == 'CNOT':
                cx += len(instr.targets_copy()) // 2
                vol += len(instr.targets_copy()) // 2
            elif instr.name in ['H', 'S', 'X', 'Y', 'Z', 'I']:
                 vol += len(instr.targets_copy())
            elif instr.name == 'CZ':
                 # CZ counts as 1 CX + 2 H per pair usually in decomposition, 
                 # but here we count instructions.
                 # If the file has CZ, we should count it as 1 or decompose.
                 # But my generator converted CZ to CX.
                 vol += len(instr.targets_copy()) // 2
            
        print(f'CX count in file: {cx}')
        
    except Exception as e:
        print(f'Error: {e}')
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    check()
